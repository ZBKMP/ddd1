<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import { useAccountStore } from '@/stores/account'
import { getCurrentUser, updateAvatar } from '@/services/account'
import { uploadImage } from '@/services/upload-file'

const MAX_SIZE_MB = 15
const ALLOWED_EXT = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'svg']
const ACCEPT_IMAGE = '.jpg,.jpeg,.png,.webp,.gif,.svg'

const props = defineProps({
  visible: { type: Boolean, required: true },
})
const emits = defineEmits(['update:visible'])

const accountStore = useAccountStore()
const fileInputRef = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const isDragOver = ref(false)

/** 数据库中已保存的头像 URL */
const savedAvatarUrl = ref('')
/** 本地待上传文件的预览（blob URL） */
const localPreviewUrl = ref('')
const selectedFile = ref<File | null>(null)

const avatarFallback = computed(() => accountStore.account.name?.[0] || '?')
const displayPreview = computed(() => localPreviewUrl.value || savedAvatarUrl.value)
const hasPendingFile = computed(() => !!selectedFile.value)
const savedUrlHint = computed(() => {
  const url = savedAvatarUrl.value
  if (!url) return '尚未设置头像'
  return url.length > 56 ? `${url.slice(0, 56)}...` : url
})

let blobPreviewUrl = ''

const revokeBlobPreview = () => {
  if (blobPreviewUrl) {
    URL.revokeObjectURL(blobPreviewUrl)
    blobPreviewUrl = ''
  }
}

const syncFromAccount = () => {
  revokeBlobPreview()
  selectedFile.value = null
  localPreviewUrl.value = ''
  savedAvatarUrl.value = accountStore.account.avatar || ''
}

watch(
  () => props.visible,
  (visible) => {
    if (visible) syncFromAccount()
  },
)

onBeforeUnmount(() => revokeBlobPreview())

const handleClose = () => {
  if (uploading.value) return
  syncFromAccount()
  emits('update:visible', false)
}

const validateFile = (file: File): string | null => {
  const ext = file.name.includes('.') ? file.name.split('.').pop()!.toLowerCase() : ''
  if (!ALLOWED_EXT.includes(ext)) {
    return `仅支持 ${ALLOWED_EXT.join('、')} 格式`
  }
  if (file.size > MAX_SIZE_MB * 1024 * 1024) {
    return `图片不能超过 ${MAX_SIZE_MB}MB`
  }
  return null
}

const applySelectedFile = (file: File) => {
  const err = validateFile(file)
  if (err) {
    Message.error(err)
    return
  }
  revokeBlobPreview()
  selectedFile.value = file
  blobPreviewUrl = URL.createObjectURL(file)
  localPreviewUrl.value = blobPreviewUrl
}

const onNativeFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) applySelectedFile(file)
  input.value = ''
}

const openFileDialog = () => {
  if (uploading.value) return
  fileInputRef.value?.click()
}

const onDrop = (event: DragEvent) => {
  isDragOver.value = false
  if (uploading.value) return
  const file = event.dataTransfer?.files?.[0]
  if (file) applySelectedFile(file)
}

const clearSelection = () => {
  revokeBlobPreview()
  selectedFile.value = null
  localPreviewUrl.value = ''
}

/** 1. 上传原图到腾讯云 COS；2. 将返回的图片 URL 写入账号表 */
const handleConfirmUpload = async () => {
  if (!selectedFile.value) {
    Message.warning('请先选择要上传的图片')
    return
  }

  try {
    uploading.value = true
    const uploadResp = await uploadImage(selectedFile.value)
    const imageUrl = uploadResp.data.image_url

    const updateResp = await updateAvatar(imageUrl)
    Message.success(updateResp.message || '头像已保存')

    const resp = await getCurrentUser()
    accountStore.update(resp.data)

    savedAvatarUrl.value = imageUrl
    clearSelection()
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '上传失败，请稍后重试'
    Message.error(message)
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <a-modal
    :visible="visible"
    title="上传头像"
    :width="480"
    :mask-closable="!uploading"
    :closable="!uploading"
    @cancel="handleClose"
  >
    <div class="flex flex-col gap-4">
      <a-alert type="info" show-icon>
        原始图片将上传至腾讯云 COS 存储；系统返回的图片访问地址会保存到您的账号信息中，作为头像展示。
      </a-alert>

      <div class="flex flex-col items-center gap-3">
        <a-avatar :size="104" class="text-3xl bg-blue-700" :image-url="displayPreview">
          {{ avatarFallback }}
        </a-avatar>
        <span class="text-xs text-gray-500">预览</span>
      </div>

      <input
        ref="fileInputRef"
        type="file"
        class="hidden"
        :accept="ACCEPT_IMAGE"
        @change="onNativeFileChange"
      />

      <div
        class="upload-dropzone"
        :class="{ 'upload-dropzone--active': isDragOver, 'upload-dropzone--disabled': uploading }"
        @click="openFileDialog"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="onDrop"
      >
        <icon-upload class="text-3xl text-gray-400 mb-2" />
        <p class="text-gray-800 font-medium m-0 mb-1">点击或拖拽图片到此处</p>
        <p class="text-xs text-gray-500 m-0">
          JPG / PNG / WEBP / GIF / SVG，不超过 {{ MAX_SIZE_MB }}MB
        </p>
        <p v-if="selectedFile" class="text-sm text-blue-600 mt-3 m-0">
          已选择：{{ selectedFile.name }}
        </p>
      </div>

      <div class="rounded-lg bg-gray-50 px-3 py-2 text-xs text-gray-600">
        <div class="font-medium text-gray-700 mb-1">当前头像地址（数据库）</div>
        <div class="break-all">{{ savedUrlHint }}</div>
      </div>
    </div>

    <template #footer>
      <a-button :disabled="uploading" @click="handleClose">取消</a-button>
      <a-button v-if="hasPendingFile" :disabled="uploading" @click="clearSelection">
        重新选择
      </a-button>
      <a-button type="primary" :loading="uploading" :disabled="!hasPendingFile" @click="handleConfirmUpload">
        上传并保存
      </a-button>
    </template>
  </a-modal>
</template>

<style scoped>
.upload-dropzone {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 28px 16px;
  text-align: center;
  cursor: pointer;
  transition:
    border-color 0.2s,
    background-color 0.2s;
}

.upload-dropzone:hover:not(.upload-dropzone--disabled) {
  border-color: #3b82f6;
  background-color: #f8fafc;
}

.upload-dropzone--active {
  border-color: #2563eb;
  background-color: #eff6ff;
}

.upload-dropzone--disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
