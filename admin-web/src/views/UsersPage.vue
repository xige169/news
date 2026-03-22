<template>
  <div>
    <div class="page-toolbar">
      <div>
        <h2 class="section-title">用户管理</h2>
        <p class="section-copy">筛选账号并调整后台权限角色，前后台共用同一登录体系。</p>
      </div>
    </div>

    <section class="page-card page-table-card">
      <el-form :inline="true" :model="filters" class="news-filter">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="用户名 / 昵称" clearable />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filters.role" placeholder="全部角色" clearable style="width: 160px">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">筛选</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="users" stripe v-loading="loading">
        <el-table-column prop="username" label="用户名" min-width="180" />
        <el-table-column prop="nickname" label="昵称" min-width="180">
          <template #default="{ row }">
            {{ row.nickname || '未设置昵称' }}
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="注册时间" min-width="200" />
        <el-table-column label="角色" width="180">
          <template #default="{ row }">
            <el-select :model-value="row.role" style="width: 140px" @change="(value) => handleRoleChange(row, value)">
              <el-option label="普通用户" value="user" />
              <el-option label="管理员" value="admin" />
            </el-select>
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
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { fetchUsers, updateUserRole } from '../services/users.js'

const loading = ref(false)
const users = ref([])

const filters = reactive({
  keyword: '',
  role: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
})

const loadUsers = async () => {
  loading.value = true
  try {
    const payload = await fetchUsers({
      page: pagination.page,
      pageSize: pagination.pageSize,
      keyword: filters.keyword,
      role: filters.role,
    })
    users.value = payload.list || []
    pagination.total = payload.total || 0
  } catch (error) {
    users.value = []
    pagination.total = 0
    ElMessage.error(error instanceof Error ? error.message : '用户加载失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  pagination.page = 1
  await loadUsers()
}

const handleReset = async () => {
  filters.keyword = ''
  filters.role = ''
  pagination.page = 1
  await loadUsers()
}

const handlePageChange = async (page) => {
  pagination.page = page
  await loadUsers()
}

const handleRoleChange = async (row, role) => {
  try {
    await updateUserRole(row.id, role)
    row.role = role
    ElMessage.success('角色已更新')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '角色更新失败')
    await loadUsers()
  }
}

onMounted(loadUsers)
</script>
