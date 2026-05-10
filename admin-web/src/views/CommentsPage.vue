<template>
  <div class="comments">
    <PageToolbar>
      <template #filters>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索评论内容、用户名或新闻"
          clearable
          size="default"
          style="width: 280px"
          @keydown.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-input
          v-model.number="filters.newsId"
          placeholder="新闻 ID"
          clearable
          size="default"
          type="number"
          style="width: 140px"
          @keydown.enter="onSearch"
          @clear="onSearch"
        />
      </template>
      <template #actions>
        <span class="comments__hint">共 {{ total }} 条评论</span>
      </template>
    </PageToolbar>

    <div class="comments__table page-card">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column label="评论内容" min-width="280">
          <template #default="{ row }">
            <span v-if="row.isDeleted" class="comments__deleted">[已删除]</span>
            <span v-else class="comments__content">{{ row.content }}</span>
          </template>
        </el-table-column>
        <el-table-column label="所属新闻" min-width="180">
          <template #default="{ row }">
            <span class="comments__news">{{ row.newsTitle || `#${row.newsId}` }}</span>
            <span class="comments__news-id">#{{ row.newsId }}</span>
          </template>
        </el-table-column>
        <el-table-column label="评论者" prop="userName" width="140" />
        <el-table-column label="父评论" width="100">
          <template #default="{ row }">
            <span v-if="row.parentId">#{{ row.parentId }}</span>
            <span v-else class="comments__muted">—</span>
          </template>
        </el-table-column>
        <el-table-column label="点赞" prop="likeCount" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.isDeleted" type="info" size="small">已删除</el-tag>
            <el-tag v-else type="success" size="small">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-popconfirm
              v-if="!row.isDeleted"
              title="确认删除该评论？"
              @confirm="onDelete(row)"
            >
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
            <el-button v-else link disabled>已删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="comments__pagination">
        <el-pagination
          background
          layout="total, prev, pager, next, sizes"
          :total="total"
          :current-page="page"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          @current-change="onPageChange"
          @size-change="onSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import {
  ElButton,
  ElIcon,
  ElInput,
  ElMessage,
  ElPagination,
  ElPopconfirm,
  ElTable,
  ElTableColumn,
  ElTag
} from 'element-plus'
import { Search } from '@element-plus/icons-vue'

import PageToolbar from '../components/common/PageToolbar.vue'
import { fetchComments, deleteComment } from '../services/comments.js'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const filters = reactive({
  keyword: '',
  newsId: null
})

const formatDate = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const load = async () => {
  loading.value = true
  try {
    const data = await fetchComments({
      page: page.value,
      pageSize: pageSize.value,
      keyword: filters.keyword || undefined,
      newsId: filters.newsId || undefined
    })
    list.value = data?.list || []
    total.value = data?.total || 0
  } catch (err) {
    ElMessage.error(err?.message || '加载评论失败')
  } finally {
    loading.value = false
  }
}

const onSearch = () => {
  page.value = 1
  load()
}

const onPageChange = (next) => {
  page.value = next
  load()
}

const onSizeChange = (size) => {
  pageSize.value = size
  page.value = 1
  load()
}

const onDelete = async (row) => {
  try {
    await deleteComment(row.id)
    ElMessage.success('已删除')
    load()
  } catch (err) {
    ElMessage.error(err?.message || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.comments__hint {
  font-size: var(--fs-13);
  color: var(--text-secondary);
}

.comments__table {
  padding: var(--sp-3) var(--sp-3) var(--sp-4);
}

.comments__content {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

.comments__news {
  display: block;
  color: var(--text-primary);
  font-size: var(--fs-13);
  line-height: 1.4;
}

.comments__news-id {
  display: block;
  color: var(--text-muted);
  font-size: var(--fs-12);
}

.comments__deleted {
  color: var(--text-muted);
  font-style: italic;
}

.comments__muted {
  color: var(--text-muted);
}

.comments__pagination {
  display: flex;
  justify-content: flex-end;
  padding: var(--sp-3) var(--sp-2) 0;
}
</style>
