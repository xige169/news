<template>
  <section class="page-card page-table-card">
    <div class="section-heading">
      <div>
        <h2 class="section-title">{{ isEditMode ? '编辑新闻' : '创建新闻' }}</h2>
        <p class="section-copy">稿件必须通过完整表单创建，不再保留“只输标题快速建稿”的半成品流程。</p>
      </div>
    </div>

    <el-form label-position="top" :model="form" class="editor-form">
      <div class="editor-grid">
        <el-form-item label="新闻标题">
          <el-input v-model="form.title" placeholder="请输入新闻标题" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="form.author" placeholder="请输入作者或来源" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.categoryId" placeholder="请选择分类">
            <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已下线" value="offline" />
          </el-select>
        </el-form-item>
        <el-form-item label="封面图">
          <el-input v-model="form.image" placeholder="请输入图片 URL" />
        </el-form-item>
        <el-form-item label="发布时间">
          <el-date-picker v-model="form.publishTime" type="datetime" placeholder="选择发布时间" value-format="YYYY-MM-DDTHH:mm:ss" />
        </el-form-item>
      </div>

      <el-form-item label="摘要">
        <el-input v-model="form.description" type="textarea" :rows="3" maxlength="500" show-word-limit />
      </el-form-item>

      <el-form-item label="正文">
        <el-input v-model="form.content" type="textarea" :rows="14" placeholder="请输入完整新闻正文" />
      </el-form-item>

      <el-form-item>
        <el-switch v-model="form.isFeatured" active-text="加入推荐位" inactive-text="普通稿件" />
      </el-form-item>

      <el-space>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEditMode ? '保存修改' : '创建稿件' }}
        </el-button>
        <el-button @click="router.push('/news')">返回列表</el-button>
      </el-space>
    </el-form>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { fetchCategories } from '../services/categories.js'
import { createNews, fetchNewsDetail, updateNews } from '../services/news.js'

const route = useRoute()
const router = useRouter()
const submitting = ref(false)
const categories = ref([])

const form = reactive({
  title: '',
  description: '',
  content: '',
  image: '',
  author: '',
  categoryId: '',
  status: 'draft',
  isFeatured: false,
  publishTime: '',
})

const isEditMode = computed(() => Boolean(route.params.id))

const validateForm = () => {
  if (!form.title || !form.content || !form.categoryId) {
    ElMessage.warning('标题、正文和分类为必填项')
    return false
  }
  return true
}

const loadCategories = async () => {
  categories.value = await fetchCategories()
}

const loadDetail = async () => {
  if (!isEditMode.value) return
  const payload = await fetchNewsDetail(route.params.id)
  form.title = payload.title || ''
  form.description = payload.description || ''
  form.content = payload.content || ''
  form.image = payload.image || ''
  form.author = payload.author || ''
  form.categoryId = payload.categoryId || ''
  form.status = payload.status || 'draft'
  form.isFeatured = Boolean(payload.isFeatured)
  form.publishTime = payload.publishTime ? String(payload.publishTime).slice(0, 19) : ''
}

const handleSubmit = async () => {
  if (!validateForm()) return

  submitting.value = true
  try {
    const payload = {
      ...form,
      categoryId: Number(form.categoryId),
      publishTime: form.publishTime || null,
    }

    if (isEditMode.value) {
      await updateNews(route.params.id, payload)
      ElMessage.success('稿件已更新')
    } else {
      await createNews(payload)
      ElMessage.success('稿件已创建')
    }
    router.push('/news')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存失败')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    await loadCategories()
    await loadDetail()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '编辑数据加载失败')
  }
})
</script>

<style scoped>
.editor-form {
  display: grid;
  gap: 10px;
}

.editor-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 18px;
}
</style>
