<template>
  <div class="news-mgmt">
    <PageToolbar>
      <template #filters>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索标题或作者"
          clearable
          size="default"
          style="width: 240px"
          @keydown.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="filters.status"
          placeholder="状态"
          clearable
          size="default"
          style="width: 140px"
          @change="onSearch"
        >
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
          <el-option label="已下线" value="offline" />
        </el-select>

        <el-select
          v-model="filters.categoryId"
          placeholder="栏目"
          clearable
          size="default"
          style="width: 160px"
          @change="onSearch"
        >
          <el-option
            v-for="item in categories"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </template>

      <template #actions>
        <el-button type="primary" @click="$router.push('/news/create')">
          <el-icon><Plus /></el-icon>
          新建稿件
        </el-button>
      </template>

      <template v-if="selection.length" #bulk>
        <span>已选中 <strong>{{ selection.length }}</strong> 条</span>
        <el-button size="small" @click="onBulkStatus('published')">批量发布</el-button>
        <el-button size="small" @click="onBulkStatus('offline')">批量下线</el-button>
        <el-button size="small" type="danger" plain @click="onBulkDelete">批量删除</el-button>
        <el-button size="small" link @click="clearSelection">清除选择</el-button>
      </template>
    </PageToolbar>

    <div class="news-mgmt__table page-card">
      <el-table
        ref="tableRef"
        :data="list"
        v-loading="loading"
        stripe
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="44" />
        <el-table-column label="标题" min-width="280">
          <template #default="{ row }">
            <router-link :to="`/news/${row.id}/edit`" class="news-mgmt__title-link">
              {{ row.title }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="栏目" width="130">
          <template #default="{ row }">{{ categoryName(row.categoryId) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <StatusChip :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="views" label="浏览" width="80" align="right" />
        <el-table-column label="更新时间" width="160">
          <template #default="{ row }">{{ formatDate(row.updatedAt || row.publishTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="$router.push(`/news/${row.id}/edit`)">
              编辑
            </el-button>
            <el-button v-if="row.status !== 'published'" link @click="onChangeStatus(row, 'published')">
              发布
            </el-button>
            <el-button v-else link @click="onChangeStatus(row, 'offline')">
              下线
            </el-button>
            <el-popconfirm title="确认删除该稿件？" @confirm="onDelete(row)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="news-mgmt__pagination">
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
  ElMessageBox,
  ElOption,
  ElPagination,
  ElPopconfirm,
  ElSelect,
  ElTable,
  ElTableColumn
} from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'

import PageToolbar from '../components/common/PageToolbar.vue'
import StatusChip from '../components/common/StatusChip.vue'
import { fetchCategories } from '../services/categories.js'
import {
  deleteNews,
  fetchNewsList,
  updateNewsStatus
} from '../services/news.js'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const categories = ref([])
const selection = ref([])
const tableRef = ref(null)

const filters = reactive({
  keyword: '',
  status: null,
  categoryId: null
})

const categoryName = (id) => categories.value.find((c) => c.id === id)?.name || '-'

const formatDate = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const load = async () => {
  loading.value = true
  try {
    const data = await fetchNewsList({
      page: page.value,
      pageSize: pageSize.value,
      keyword: filters.keyword || undefined,
      status: filters.status || undefined,
      categoryId: filters.categoryId || undefined
    })
    list.value = data?.list || []
    total.value = data?.total || 0
  } catch (err) {
    ElMessage.error(err?.message || '加载失败')
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

const onSelectionChange = (rows) => {
  selection.value = rows
}

const clearSelection = () => {
  tableRef.value?.clearSelection()
}

const onChangeStatus = async (row, nextStatus) => {
  try {
    await updateNewsStatus(row.id, nextStatus)
    ElMessage.success('已更新')
    load()
  } catch (err) {
    ElMessage.error(err?.message || '操作失败')
  }
}

const onDelete = async (row) => {
  try {
    await deleteNews(row.id)
    ElMessage.success('已删除')
    load()
  } catch (err) {
    ElMessage.error(err?.message || '删除失败')
  }
}

const onBulkStatus = async (nextStatus) => {
  if (!selection.value.length) return
  try {
    await Promise.all(selection.value.map((row) => updateNewsStatus(row.id, nextStatus)))
    ElMessage.success('已批量更新')
    clearSelection()
    load()
  } catch (err) {
    ElMessage.error(err?.message || '批量更新失败')
  }
}

const onBulkDelete = async () => {
  if (!selection.value.length) return
  try {
    await ElMessageBox.confirm(`确认删除选中的 ${selection.value.length} 条稿件？`, '危险操作', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }
  try {
    await Promise.all(selection.value.map((row) => deleteNews(row.id)))
    ElMessage.success('已删除')
    clearSelection()
    load()
  } catch (err) {
    ElMessage.error(err?.message || '批量删除失败')
  }
}

onMounted(async () => {
  try {
    const data = await fetchCategories()
    categories.value = Array.isArray(data) ? data : data?.list || []
  } catch {
    categories.value = []
  }
  load()
})
</script>

<style scoped>
.news-mgmt__table {
  padding: var(--sp-3) var(--sp-3) var(--sp-4);
}

.news-mgmt__title-link {
  color: var(--text-primary);
  font-weight: 500;
}

.news-mgmt__title-link:hover {
  color: var(--accent);
}

.news-mgmt__pagination {
  display: flex;
  justify-content: flex-end;
  padding: var(--sp-3) var(--sp-2) 0;
}
</style>
