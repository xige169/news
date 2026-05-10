<template>
  <div class="dashboard">
    <section class="dashboard__stats">
      <article v-for="card in statCards" :key="card.label" class="stat-card">
        <span class="stat-card__label">{{ card.label }}</span>
        <strong class="stat-card__value">{{ card.value }}</strong>
        <span v-if="card.copy" class="stat-card__copy">{{ card.copy }}</span>
      </article>
    </section>

    <div class="dashboard__grid">
      <section class="dashboard__panel page-card dashboard__panel--main">
        <div class="dashboard__panel-header">
          <div>
            <h3 class="section-title">最近更新</h3>
            <p class="section-copy">最近被编辑或发布的稿件</p>
          </div>
          <el-button @click="$router.push('/news')">查看全部</el-button>
        </div>
        <el-table
          :data="summary.recentNews || []"
          v-loading="loading"
          stripe
          @row-click="onRowClick"
        >
          <el-table-column prop="title" label="标题" min-width="240" show-overflow-tooltip />
          <el-table-column label="状态" width="110">
            <template #default="{ row }">
              <StatusChip :status="row.status" />
            </template>
          </el-table-column>
          <el-table-column prop="author" label="作者" width="120" />
          <el-table-column prop="views" label="浏览" width="80" align="right" />
          <el-table-column label="更新时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.updatedAt || row.publishTime) }}
            </template>
          </el-table-column>
        </el-table>
      </section>

      <section class="dashboard__panel page-card">
        <div class="dashboard__panel-header">
          <div>
            <h3 class="section-title">状态分布</h3>
            <p class="section-copy">按发布状态聚合</p>
          </div>
        </div>
        <StatusDonut
          :data="{
            published: summary.publishedNewsTotal || 0,
            draft: summary.draftNewsTotal || 0,
            offline: summary.offlineNewsTotal || 0
          }"
        />
      </section>

      <section class="dashboard__panel page-card">
        <div class="dashboard__panel-header">
          <div>
            <h3 class="section-title">栏目稿件量</h3>
            <p class="section-copy">每个栏目下的发布数量</p>
          </div>
        </div>
        <CategoryBar :items="categories" :height="280" />
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElButton, ElMessage, ElTable, ElTableColumn } from 'element-plus'

import StatusChip from '../components/common/StatusChip.vue'
import StatusDonut from '../components/charts/StatusDonut.vue'
import CategoryBar from '../components/charts/CategoryBar.vue'
import { fetchDashboardSummary } from '../services/dashboard.js'
import { fetchCategories } from '../services/categories.js'

const router = useRouter()
const loading = ref(false)
const summary = ref({})
const categories = ref([])

const statCards = computed(() => [
  { label: '稿件总数', value: summary.value.newsTotal || 0, copy: '所有状态' },
  { label: '已发布', value: summary.value.publishedNewsTotal || 0, copy: '前台可见' },
  { label: '草稿', value: summary.value.draftNewsTotal || 0, copy: '待发布' },
  { label: '已下线', value: summary.value.offlineNewsTotal || 0, copy: '暂时下架' },
  { label: '栏目', value: summary.value.categoryTotal || 0, copy: '内容分类数' },
  { label: '用户', value: summary.value.userTotal || 0, copy: `含 ${summary.value.adminTotal || 0} 名管理员` }
])

const formatDate = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const onRowClick = (row) => {
  if (row?.id) router.push(`/news/${row.id}/edit`)
}

const load = async () => {
  loading.value = true
  try {
    const [s, c] = await Promise.all([fetchDashboardSummary(), fetchCategories()])
    summary.value = s || {}
    categories.value = Array.isArray(c) ? c : c?.list || []
  } catch (error) {
    ElMessage.error(error?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--sp-5);
}

.dashboard__stats {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: var(--sp-4);
}

.stat-card {
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--sp-4) var(--sp-5);
  display: flex;
  flex-direction: column;
  gap: var(--sp-1);
}

.stat-card__label {
  font-size: var(--fs-12);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.stat-card__value {
  font-size: var(--fs-30);
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-card__copy {
  font-size: var(--fs-12);
  color: var(--text-secondary);
}

.dashboard__grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: var(--sp-4);
}

.dashboard__panel {
  padding: var(--sp-5);
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
}

.dashboard__panel--main {
  grid-row: span 1;
}

.dashboard__panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--sp-4);
}

@media (max-width: 1280px) {
  .dashboard__stats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .dashboard__grid {
    grid-template-columns: 1fr 1fr;
  }
  .dashboard__panel--main {
    grid-column: span 2;
  }
}
</style>
