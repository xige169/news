<template>
  <div class="dashboard-page">
    <section class="dashboard-hero page-card">
      <div>
        <p class="dashboard-hero__eyebrow">DAILY OPS SNAPSHOT</p>
        <h2>新闻运营总览</h2>
        <p>聚合稿件状态、分类与权限体量，帮助编辑和运营快速判断当日盘面。</p>
      </div>
      <el-button type="primary" @click="router.push('/news/create')">新建稿件</el-button>
    </section>

    <section class="dashboard-stats">
      <article v-for="item in statCards" :key="item.label" class="dashboard-stat page-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <p>{{ item.copy }}</p>
      </article>
    </section>

    <section class="page-card page-table-card">
      <div class="section-heading">
        <div>
          <h2 class="section-title">最近更新</h2>
          <p class="section-copy">优先展示最近被编辑或发布的稿件。</p>
        </div>
      </div>

      <el-table :data="summary.recentNews || []" stripe v-loading="loading">
        <el-table-column prop="title" label="标题" min-width="260" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <span class="status-chip" :class="`status-chip--${row.status}`">
              {{ statusTextMap[row.status] || row.status }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="浏览量" width="110" />
        <el-table-column prop="author" label="作者" width="150" />
      </el-table>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { fetchDashboardSummary } from '../services/dashboard.js'

const router = useRouter()
const loading = ref(false)
const summary = ref({})

const statusTextMap = {
  published: '已发布',
  draft: '草稿',
  offline: '已下线',
}

const statCards = computed(() => [
  { label: '稿件总数', value: summary.value.newsTotal || 0, copy: '当前新闻内容池规模' },
  { label: '已发布', value: summary.value.publishedNewsTotal || 0, copy: '正在前台可见的稿件' },
  { label: '草稿', value: summary.value.draftNewsTotal || 0, copy: '待编辑和待确认稿件' },
  { label: '已下线', value: summary.value.offlineNewsTotal || 0, copy: '暂不展示但保留资料' },
  { label: '栏目数量', value: summary.value.categoryTotal || 0, copy: '导航和运营栏目结构' },
  { label: '后台管理员', value: summary.value.adminTotal || 0, copy: '具备后台权限账号数' },
])

const loadSummary = async () => {
  loading.value = true
  try {
    summary.value = await fetchDashboardSummary()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '仪表盘加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadSummary)
</script>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 20px;
}

.dashboard-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 26px 28px;
}

.dashboard-hero__eyebrow {
  margin: 0 0 10px;
  color: var(--accent);
  font-size: 11px;
  letter-spacing: 0.3em;
}

.dashboard-hero h2 {
  margin: 0;
  font-size: 30px;
}

.dashboard-hero p:last-child {
  margin: 10px 0 0;
  color: var(--text-secondary);
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.dashboard-stat {
  padding: 22px;
}

.dashboard-stat span {
  color: var(--text-secondary);
  font-size: 13px;
}

.dashboard-stat strong {
  display: block;
  margin-top: 12px;
  font-size: 34px;
}

.dashboard-stat p {
  margin: 12px 0 0;
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.6;
}
</style>
