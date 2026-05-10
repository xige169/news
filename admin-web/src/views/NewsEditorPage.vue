<template>
  <div class="news-editor">
    <header class="news-editor__header page-card">
      <div class="news-editor__header-left">
        <el-button link @click="$router.push('/news')">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <h2>{{ isEdit ? '编辑稿件' : '新建稿件' }}</h2>
        <StatusChip v-if="form.status" :status="form.status" />
      </div>
      <div class="news-editor__header-right">
        <el-button :loading="savingDraft" @click="onSave('draft')">保存草稿</el-button>
        <el-button type="primary" :loading="savingPublish" @click="onSave('published')">
          {{ form.status === 'published' ? '更新已发布' : '发布' }}
        </el-button>
      </div>
    </header>

    <div class="news-editor__body" v-loading="loading">
      <section class="news-editor__main page-card">
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
          <el-form-item label="标题" prop="title">
            <el-input
              v-model="form.title"
              size="large"
              placeholder="清晰、准确地描述新闻主题"
              maxlength="255"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="摘要" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 4 }"
              placeholder="一两句话概括新闻内容"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="正文" prop="content">
            <el-tabs v-model="contentTab" class="news-editor__tabs">
              <el-tab-pane label="编辑（Markdown）" name="edit">
                <el-input
                  v-model="form.content"
                  type="textarea"
                  :autosize="{ minRows: 18, maxRows: 32 }"
                  placeholder="支持 Markdown，标题/列表/链接/图片"
                />
              </el-tab-pane>
              <el-tab-pane label="预览" name="preview">
                <div class="news-editor__preview" v-html="renderedPreview" />
              </el-tab-pane>
            </el-tabs>
          </el-form-item>
        </el-form>
      </section>

      <aside class="news-editor__side">
        <section class="page-card news-editor__side-block">
          <h3 class="section-title">元数据</h3>

          <el-form :model="form" label-position="top">
            <el-form-item label="栏目" required>
              <el-select v-model="form.categoryId" placeholder="选择栏目" filterable>
                <el-option
                  v-for="item in categories"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="作者">
              <el-input v-model="form.author" maxlength="50" />
            </el-form-item>

            <el-form-item label="封面图 URL">
              <el-input v-model="form.image" placeholder="https://..." />
            </el-form-item>

            <el-form-item v-if="form.image" label="预览">
              <div class="news-editor__cover">
                <img :src="form.image" alt="cover" />
              </div>
            </el-form-item>

            <el-form-item label="发布时间">
              <el-date-picker
                v-model="form.publishTime"
                type="datetime"
                placeholder="留空使用当前时间"
                value-format="YYYY-MM-DDTHH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item>
              <el-checkbox v-model="form.isFeatured">设为推荐稿件</el-checkbox>
            </el-form-item>
          </el-form>
        </section>

        <section v-if="isEdit" class="page-card news-editor__side-block">
          <h3 class="section-title">危险操作</h3>
          <p class="section-copy">删除后不可恢复</p>
          <el-popconfirm title="确认删除该稿件？" @confirm="onDelete">
            <template #reference>
              <el-button type="danger" plain class="news-editor__delete">删除稿件</el-button>
            </template>
          </el-popconfirm>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import {
  ElButton,
  ElCheckbox,
  ElDatePicker,
  ElForm,
  ElFormItem,
  ElIcon,
  ElInput,
  ElMessage,
  ElMessageBox,
  ElOption,
  ElPopconfirm,
  ElSelect,
  ElTabPane,
  ElTabs
} from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

import StatusChip from '../components/common/StatusChip.vue'
import { fetchCategories } from '../services/categories.js'
import {
  createNews,
  deleteNews,
  fetchNewsDetail,
  updateNews
} from '../services/news.js'

const route = useRoute()
const router = useRouter()
const formRef = ref(null)
const contentTab = ref('edit')

const loading = ref(false)
const savingDraft = ref(false)
const savingPublish = ref(false)
const dirty = ref(false)
const initialSnapshot = ref('')

const isEdit = computed(() => Boolean(route.params.id))
const newsId = computed(() => Number(route.params.id))

const categories = ref([])

const form = reactive({
  title: '',
  description: '',
  content: '',
  image: '',
  author: '',
  categoryId: null,
  status: 'draft',
  isFeatured: false,
  publishTime: ''
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入正文', trigger: 'blur' }]
}

const renderedPreview = computed(() => {
  const raw = form.content || ''
  if (!raw) return '<p style="color:#9a9a9a">暂无内容</p>'
  return DOMPurify.sanitize(marked.parse(raw, { breaks: true, gfm: true }))
})

const snapshot = () => JSON.stringify(form)

const buildPayload = (status) => ({
  title: form.title?.trim(),
  description: form.description?.trim() || null,
  content: form.content,
  image: form.image?.trim() || null,
  author: form.author?.trim() || null,
  categoryId: form.categoryId,
  status,
  isFeatured: form.isFeatured,
  publishTime: form.publishTime || null
})

const populate = (detail) => {
  form.title = detail?.title || ''
  form.description = detail?.description || ''
  form.content = detail?.content || ''
  form.image = detail?.image || ''
  form.author = detail?.author || ''
  form.categoryId = detail?.categoryId || null
  form.status = detail?.status || 'draft'
  form.isFeatured = Boolean(detail?.isFeatured)
  form.publishTime = detail?.publishTime || ''
  initialSnapshot.value = snapshot()
  dirty.value = false
}

const watchDirty = () => {
  setInterval(() => {
    dirty.value = snapshot() !== initialSnapshot.value
  }, 800)
}

const onSave = async (targetStatus) => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  if (!form.categoryId) {
    ElMessage.error('请选择栏目')
    return
  }
  if (targetStatus === 'draft') savingDraft.value = true
  else savingPublish.value = true
  try {
    const payload = buildPayload(targetStatus)
    if (isEdit.value) {
      const updated = await updateNews(newsId.value, payload)
      populate(updated)
      ElMessage.success('已保存')
    } else {
      const created = await createNews(payload)
      ElMessage.success('已创建')
      router.replace(`/news/${created.id}/edit`)
    }
  } catch (err) {
    ElMessage.error(err?.message || '保存失败')
  } finally {
    savingDraft.value = false
    savingPublish.value = false
  }
}

const onDelete = async () => {
  try {
    await deleteNews(newsId.value)
    ElMessage.success('已删除')
    dirty.value = false
    router.replace('/news')
  } catch (err) {
    ElMessage.error(err?.message || '删除失败')
  }
}

const loadDetail = async () => {
  if (!isEdit.value) {
    initialSnapshot.value = snapshot()
    return
  }
  loading.value = true
  try {
    const detail = await fetchNewsDetail(newsId.value)
    populate(detail)
  } catch (err) {
    ElMessage.error(err?.message || '加载稿件失败')
  } finally {
    loading.value = false
  }
}

onBeforeRouteLeave(async () => {
  if (!dirty.value) return true
  try {
    await ElMessageBox.confirm('当前修改未保存，确认离开？', '未保存', {
      confirmButtonText: '离开',
      cancelButtonText: '继续编辑',
      type: 'warning'
    })
    return true
  } catch {
    return false
  }
})

let dirtyTimer = null
onMounted(async () => {
  try {
    const data = await fetchCategories()
    categories.value = Array.isArray(data) ? data : data?.list || []
  } catch {
    categories.value = []
  }
  await loadDetail()
  dirtyTimer = setInterval(() => {
    dirty.value = snapshot() !== initialSnapshot.value
  }, 800)
})

onBeforeUnmount(() => {
  if (dirtyTimer) clearInterval(dirtyTimer)
})
</script>

<style scoped>
.news-editor__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-3) var(--sp-5);
  margin-bottom: var(--sp-4);
}

.news-editor__header-left {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}

.news-editor__header-left h2 {
  font-size: var(--fs-18);
}

.news-editor__header-right {
  display: flex;
  gap: var(--sp-2);
}

.news-editor__body {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--sp-4);
  align-items: start;
}

.news-editor__main {
  padding: var(--sp-5);
}

.news-editor__side {
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
}

.news-editor__side-block {
  padding: var(--sp-5);
}

.news-editor__tabs {
  width: 100%;
}

.news-editor__preview {
  min-height: 320px;
  padding: var(--sp-4);
  background: var(--bg-elevated);
  border-radius: var(--radius-md);
  font-size: var(--fs-14);
  line-height: 1.7;
}

.news-editor__preview :deep(h1),
.news-editor__preview :deep(h2),
.news-editor__preview :deep(h3) {
  margin: 16px 0 8px;
}

.news-editor__preview :deep(p) {
  margin-bottom: 12px;
}

.news-editor__cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--bg-elevated);
}

.news-editor__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.news-editor__delete {
  width: 100%;
  margin-top: var(--sp-3);
}

@media (max-width: 1280px) {
  .news-editor__body {
    grid-template-columns: 1fr;
  }
}
</style>
