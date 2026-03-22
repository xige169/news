<template>
  <div>
    <div class="page-toolbar">
      <div>
        <h2 class="section-title">新闻管理</h2>
        <p class="section-copy">标准后台视图管理稿件筛选、编辑、上下线与删除。</p>
      </div>
      <el-button type="primary" @click="router.push('/news/create')">新建新闻</el-button>
    </div>

    <section class="page-card page-table-card">
      <el-form :inline="true" :model="filters" class="news-filter">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="标题 / 简介 / 作者" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已下线" value="offline" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filters.categoryId" placeholder="全部分类" clearable style="width: 160px">
            <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">筛选</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="newsList" stripe v-loading="loading">
        <el-table-column label="稿件" min-width="380">
          <template #default="{ row }">
            <div class="news-row">
              <img v-if="row.image" :src="row.image" alt="" class="list-cover" />
              <div class="title-cell">
                <strong>{{ row.title }}</strong>
                <span>{{ row.summary || row.description || '暂无摘要' }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <span class="status-chip" :class="`status-chip--${row.status}`">
              {{ statusTextMap[row.status] || row.status }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template #default="{ row }">
            {{ categoryMap.get(row.categoryId) || `#${row.categoryId}` }}
          </template>
        </el-table-column>
        <el-table-column prop="views" label="浏览量" width="110" />
        <el-table-column label="推荐位" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isFeatured ? 'danger' : 'info'">{{ row.isFeatured ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-space wrap>
              <el-button link type="primary" @click="router.push(`/news/${row.id}/edit`)">编辑</el-button>
              <el-button link @click="handleStatusChange(row, row.status === 'published' ? 'offline' : 'published')">
                {{ row.status === 'published' ? '下线' : '发布' }}
              </el-button>
              <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-row">
        <span class="page-toolbar__meta">共 {{ pagination.total }} 条</span>
        <el-pagination
          background
          layout="prev, pager, next"
          :current-page="pagination.page"
          :page-size="pagination.pageSize"
          :total="pagination.total"
          @current-change="handlePageChange"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { fetchCategories } from '../services/categories.js'
import { deleteNews, fetchNewsList, updateNewsStatus } from '../services/news.js'

const router = useRouter()
const loading = ref(false)
const categories = ref([])
const newsList = ref([])

const filters = reactive({
  keyword: '',
  status: '',
  categoryId: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const statusTextMap = {
  published: '已发布',
  draft: '草稿',
  offline: '已下线',
}

const categoryMap = computed(() => new Map(categories.value.map((item) => [item.id, item.name])))

const loadCategories = async () => {
  categories.value = await fetchCategories()
}

const loadNews = async () => {
  loading.value = true
  try {
    const payload = await fetchNewsList({
      page: pagination.page,
      pageSize: pagination.pageSize,
      keyword: filters.keyword,
      status: filters.status,
      categoryId: filters.categoryId,
    })
    newsList.value = payload.list || []
    pagination.total = payload.total || 0
  } catch (error) {
    newsList.value = []
    pagination.total = 0
    ElMessage.error(error instanceof Error ? error.message : '新闻列表加载失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  pagination.page = 1
  await loadNews()
}

const handleReset = async () => {
  filters.keyword = ''
  filters.status = ''
  filters.categoryId = ''
  pagination.page = 1
  await loadNews()
}

const handlePageChange = async (page) => {
  pagination.page = page
  await loadNews()
}

const handleStatusChange = async (row, nextStatus) => {
  try {
    await updateNewsStatus(row.id, nextStatus)
    ElMessage.success(nextStatus === 'published' ? '稿件已发布' : '稿件已下线')
    await loadNews()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '状态更新失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除《${row.title}》吗？`, '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteNews(row.id)
    ElMessage.success('新闻已删除')
    await loadNews()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error instanceof Error ? error.message : '删除失败')
    }
  }
}

onMounted(async () => {
  try {
    await loadCategories()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '分类加载失败')
  }
  await loadNews()
})
</script>

<style scoped>
.news-filter {
  margin-bottom: 20px;
}

.news-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.pagination-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 18px;
}
</style>
