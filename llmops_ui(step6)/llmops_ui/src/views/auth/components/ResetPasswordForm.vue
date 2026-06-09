<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Message, type ValidatedError } from '@arco-design/web-vue'
import { resetPassword } from '@/services/auth'

const PASSWORD_PATTERN = /^(?=.*[a-zA-Z])(?=.*\d).{8,16}$/

const errorMessage = ref('')
const loading = ref(false)
const resetForm = reactive({
  email: '',
  oldPassword: '',
  password: '',
  confirmPassword: '',
})
const router = useRouter()

const clearPasswordFields = () => {
  resetForm.oldPassword = ''
  resetForm.password = ''
  resetForm.confirmPassword = ''
}

const handleSubmit = async ({ errors }: { errors: Record<string, ValidatedError> | undefined }) => {
  if (errors) return

  if (!resetForm.oldPassword) {
    errorMessage.value = '请输入原密码'
    return
  }
  if (!PASSWORD_PATTERN.test(resetForm.password)) {
    errorMessage.value = '新密码须 8-16 位，且包含字母和数字'
    return
  }
  if (resetForm.password !== resetForm.confirmPassword) {
    errorMessage.value = '两次输入的新密码不一致'
    return
  }

  try {
    loading.value = true
    errorMessage.value = ''
    const resp = await resetPassword(resetForm.email, resetForm.oldPassword, resetForm.password)
    Message.success(resp.message || '密码重置成功')
    await router.replace({ name: 'auth-login' })
  } catch (error: any) {
    errorMessage.value = error.message || '密码重置失败，请稍后重试'
    clearPasswordFields()
  } finally {
    loading.value = false
  }
}

const goLogin = () => router.replace({ name: 'auth-login' })
</script>

<template>
  <div class="">
    <div class="text-gray-900 font-bold text-2xl leading-8">重置密码</div>
    <p class="text-base leading-6 text-gray-600">输入注册邮箱、原密码并设置新密码</p>
    <div class="h-8 text-red-700 leading-8 line-clamp-1">{{ errorMessage }}</div>
    <a-form
      :model="resetForm"
      @submit="handleSubmit"
      layout="vertical"
      size="large"
      class="flex flex-col w-full"
    >
      <a-form-item
        field="email"
        :rules="[{ type: 'email', required: true, message: '请输入合法的注册邮箱' }]"
        :validate-trigger="['change', 'blur']"
        hide-label
      >
        <a-input v-model="resetForm.email" size="large" placeholder="注册邮箱">
          <template #prefix>
            <icon-user />
          </template>
        </a-input>
      </a-form-item>
      <a-form-item
        field="oldPassword"
        :rules="[{ required: true, message: '原密码不能为空' }]"
        :validate-trigger="['change', 'blur']"
        hide-label
      >
        <a-input-password v-model="resetForm.oldPassword" size="large" placeholder="原密码">
          <template #prefix>
            <icon-lock />
          </template>
        </a-input-password>
      </a-form-item>
      <a-form-item
        field="password"
        :rules="[
          { required: true, message: '新密码不能为空' },
          {
            match: PASSWORD_PATTERN,
            message: '密码须 8-16 位，且包含字母和数字',
          },
        ]"
        :validate-trigger="['change', 'blur']"
        hide-label
      >
        <a-input-password v-model="resetForm.password" size="large" placeholder="新密码">
          <template #prefix>
            <icon-lock />
          </template>
        </a-input-password>
      </a-form-item>
      <a-form-item
        field="confirmPassword"
        :rules="[{ required: true, message: '请再次输入新密码' }]"
        :validate-trigger="['change', 'blur']"
        hide-label
      >
        <a-input-password
          v-model="resetForm.confirmPassword"
          size="large"
          placeholder="确认新密码"
        >
          <template #prefix>
            <icon-lock />
          </template>
        </a-input-password>
      </a-form-item>
      <a-space :size="16" direction="vertical">
        <a-button :loading="loading" size="large" type="primary" html-type="submit" long>
          确认重置
        </a-button>
        <a-button size="large" type="text" long @click="goLogin">返回登录</a-button>
      </a-space>
    </a-form>
  </div>
</template>

<style scoped></style>
