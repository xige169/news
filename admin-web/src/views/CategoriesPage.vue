<template>
  <div>
    <div class="page-toolbar">
      <div>
        <h2 class="section-title">分类管理</h2>
        <p class="section-copy">维护前台栏目结构，并显示每个栏目当前稿件数。</p>
      </div>
      <el-button type="primary" @click="openDialog()">新增分类</el-button>
    </div>

    <section class="page-card page-table-card">
      <el-table :data="categories" stripe v-loading="loading">
        <el-table-column prop="name" label="分类名称" min-width="240" />
        <el-table-column prop="sortOrder" label="排序" width="140" />
        <el-table-column prop="newsCount" label="稿件数" width="140" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增分类' : '编辑分类'" width="420px">
      <el-form label-position="top" :model="dialogForm">
        <el-form-item label="分类名称">
          <el-input v-model="dialogForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="dialogForm.sortOrder" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { createCategory, deleteCategory, fetchCategories, updateCategory } from '../services/categories.js'

const loading = ref(false)
const saving = ref(false)
const categories = ref([])
const dialogVisible = ref(false)
const dialogMode = ref('create')
const editingId = ref(null)

const dialogForm = reactive({
  name: '',
  sortOrder: 0,
})

const loadCategories = async () => {
  loading.value = true
  try {
    categories.value = await fetchCategories()
  } catch (error) {
    categories.value = []
    ElMessage.error(error instanceof Error ? error.message : '分类加载失败')
  } finally {
    loading.value = false
  }
}

const openDialog = (row = null) => {
  dialogMode.value = row ? 'edit' : 'create'
  editingId.value = row?.id || null
  dialogForm.name = row?.name || ''
  dialogForm.sortOrder = row?.sortOrder || 0
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!dialogForm.name) {
    ElMessage.warning('请输入分类名称')
    return
  }

  saving.value = true
  try {
    const payload = {
      name: dialogForm.name,
      sortOrder: dialogForm.sortOrder,
    }
    if (dialogMode.value === 'edit' && editingId.value) {
      await updateCategory(editingId.value, payload)
      ElMessage.success('分类已更新')
    } else {
      await createCategory(payload)
      ElMessage.success('分类已创建')
    }
    dialogVisible.value = false
    await loadCategories()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '分类保存失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除分类「${row.name}」吗？`, '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteCategory(row.id)
    ElMessage.success('分类已删除')
    await loadCategories()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error instanceof Error ? error.message : '删除失败')
    }
  }
}

onMounted(loadCategories)
</script>
