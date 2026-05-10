<template>
  <div class="categories">
    <PageToolbar>
      <template #filters>
        <span class="categories__hint">共 {{ list.length }} 个栏目</span>
      </template>
      <template #actions>
        <el-button type="primary" @click="onCreateOpen">
          <el-icon><Plus /></el-icon>
          新建栏目
        </el-button>
      </template>
    </PageToolbar>

    <div class="categories__table page-card">
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="name" label="名称" min-width="220">
          <template #default="{ row }">
            <el-input
              v-if="editingId === row.id"
              v-model="editingForm.name"
              size="small"
              maxlength="50"
            />
            <span v-else>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="sortOrder" label="排序" width="120">
          <template #default="{ row }">
            <el-input-number
              v-if="editingId === row.id"
              v-model="editingForm.sortOrder"
              size="small"
              :min="0"
            />
            <span v-else>{{ row.sortOrder ?? 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="newsCount" label="关联稿件数" width="140" align="right" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <template v-if="editingId === row.id">
              <el-button link type="primary" :loading="saving" @click="onEditSave">保存</el-button>
              <el-button link @click="onEditCancel">取消</el-button>
            </template>
            <template v-else>
              <el-button link type="primary" @click="onEditOpen(row)">编辑</el-button>
              <el-popconfirm
                :title="`删除栏目 ${row.name}？${row.newsCount ? '该栏目下还有稿件！' : ''}`"
                @confirm="onDelete(row)"
              >
                <template #reference>
                  <el-button link type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="createDialogVisible" title="新建栏目" width="420px" align-center>
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-position="top">
        <el-form-item label="名称" prop="name">
          <el-input v-model="createForm.name" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="排序" prop="sortOrder">
          <el-input-number v-model="createForm.sortOrder" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onCreateSubmit">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import {
  ElButton,
  ElDialog,
  ElForm,
  ElFormItem,
  ElIcon,
  ElInput,
  ElInputNumber,
  ElMessage,
  ElPopconfirm,
  ElTable,
  ElTableColumn
} from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

import PageToolbar from '../components/common/PageToolbar.vue'
import {
  createCategory,
  deleteCategory,
  fetchCategories,
  updateCategory
} from '../services/categories.js'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const editingId = ref(null)
const editingForm = reactive({ name: '', sortOrder: 0 })

const createDialogVisible = ref(false)
const createForm = reactive({ name: '', sortOrder: 0 })
const createFormRef = ref(null)
const createRules = {
  name: [{ required: true, message: '请输入栏目名称', trigger: 'blur' }]
}

const load = async () => {
  loading.value = true
  try {
    const data = await fetchCategories()
    list.value = Array.isArray(data) ? data : data?.list || []
  } catch (err) {
    ElMessage.error(err?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const onEditOpen = (row) => {
  editingId.value = row.id
  editingForm.name = row.name
  editingForm.sortOrder = row.sortOrder ?? 0
}

const onEditCancel = () => {
  editingId.value = null
}

const onEditSave = async () => {
  if (!editingForm.name.trim()) {
    ElMessage.error('请输入栏目名称')
    return
  }
  saving.value = true
  try {
    await updateCategory(editingId.value, {
      name: editingForm.name.trim(),
      sortOrder: editingForm.sortOrder
    })
    ElMessage.success('已更新')
    editingId.value = null
    load()
  } catch (err) {
    ElMessage.error(err?.message || '更新失败')
  } finally {
    saving.value = false
  }
}

const onDelete = async (row) => {
  try {
    await deleteCategory(row.id)
    ElMessage.success('已删除')
    load()
  } catch (err) {
    ElMessage.error(err?.message || '删除失败')
  }
}

const onCreateOpen = () => {
  createForm.name = ''
  createForm.sortOrder = 0
  createDialogVisible.value = true
}

const onCreateSubmit = async () => {
  try {
    await createFormRef.value?.validate()
  } catch {
    return
  }
  saving.value = true
  try {
    await createCategory({ name: createForm.name.trim(), sortOrder: createForm.sortOrder })
    ElMessage.success('已创建')
    createDialogVisible.value = false
    load()
  } catch (err) {
    ElMessage.error(err?.message || '创建失败')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.categories__hint {
  font-size: var(--fs-13);
  color: var(--text-secondary);
}

.categories__table {
  padding: var(--sp-3) var(--sp-3) var(--sp-4);
}
</style>
