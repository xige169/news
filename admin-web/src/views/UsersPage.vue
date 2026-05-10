<template>
  <div class="users">
    <PageToolbar>
      <template #filters>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索用户名或邮箱"
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
          v-model="filters.role"
          placeholder="角色"
          clearable
          size="default"
          style="width: 140px"
          @change="onSearch"
        >
          <el-option label="全部" :value="null" />
          <el-option label="管理员" value="admin" />
          <el-option label="普通用户" value="user" />
        </el-select>
      </template>
      <template #actions>
        <span class="users__hint">共 {{ total }} 名用户</span>
      </template>
    </PageToolbar>

    <div class="users__table page-card">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column label="用户" min-width="220">
          <template #default="{ row }">
            <div class="users__cell-user">
              <span class="users__avatar">{{ initial(row) }}</span>
              <div class="users__cell-text">
                <strong>{{ row.username }}</strong>
                <span v-if="row.nickname && row.nickname !== row.username">
                  {{ row.nickname }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="220" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <StatusChip :status="row.role" />
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="180">
          <template #default="{ row }">{{ formatDate(row.createdAt || row.registerTime) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.role === 'user'"
              link
              type="primary"
              @click="onChangeRole(row, 'admin')"
            >
              提升为管理员
            </el-button>
            <el-button
              v-else-if="row.role === 'admin'"
              link
              type="warning"
              @click="onChangeRole(row, 'user')"
            >
              撤销管理员
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="users__pagination">
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
  ElSelect,
  ElTable,
  ElTableColumn
} from 'element-plus'
import { Search } from '@element-plus/icons-vue'

import PageToolbar from '../components/common/PageToolbar.vue'
import StatusChip from '../components/common/StatusChip.vue'
import { fetchUsers, updateUserRole } from '../services/users.js'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const filters = reactive({
  keyword: '',
  role: null
})

const initial = (row) => (row.username || '?').slice(0, 1).toUpperCase()

const formatDate = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const load = async () => {
  loading.value = true
  try {
    const data = await fetchUsers({
      page: page.value,
      pageSize: pageSize.value,
      keyword: filters.keyword || undefined,
      role: filters.role || undefined
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

const onChangeRole = async (row, nextRole) => {
  const action = nextRole === 'admin' ? '提升为管理员' : '撤销管理员权限'
  try {
    await ElMessageBox.confirm(
      `确认将「${row.username}」${action}？此操作会立即生效。`,
      '修改用户角色',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }
  try {
    await updateUserRole(row.id, nextRole)
    ElMessage.success('角色已更新')
    load()
  } catch (err) {
    ElMessage.error(err?.message || '更新失败')
  }
}

onMounted(load)
</script>

<style scoped>
.users__hint {
  font-size: var(--fs-13);
  color: var(--text-secondary);
}

.users__table {
  padding: var(--sp-3) var(--sp-3) var(--sp-4);
}

.users__cell-user {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}

.users__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-soft);
  color: var(--accent);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: var(--fs-13);
}

.users__cell-text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.users__cell-text strong {
  font-size: var(--fs-14);
  color: var(--text-primary);
}

.users__cell-text span {
  font-size: var(--fs-12);
  color: var(--text-muted);
}

.users__pagination {
  display: flex;
  justify-content: flex-end;
  padding: var(--sp-3) var(--sp-2) 0;
}
</style>
