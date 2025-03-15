<template>
  <!-- 注册页面的容器 -->
  <div class="register-container">
    <!-- 注册卡片，使用Element UI的el-card组件 -->
    <el-card class="register-card">
      <template #header>
        <!-- 头部模板区域，用于放置标题 -->
        <h2>注册</h2>
      </template>
      
      <!-- 注册表单 -->
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="80px"
        @submit.prevent="handleSubmit"
      >
        <!-- 用户名输入框 -->
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="formData.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <!-- 邮箱输入框 -->
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="formData.email"
            placeholder="请输入邮箱"
            :prefix-icon="Message"
          />
        </el-form-item>
        
        <!-- 密码输入框 -->
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <!-- 确认密码输入框 -->
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="formData.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <!-- 提交按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            class="submit-btn"
          >
            注册
          </el-button>
        </el-form-item>
        
        <!-- 表单底部链接 -->
        <div class="form-footer">
          <a href="#" @click.prevent="goToRegister">已有账号，立即登录</a>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'; // 引入Vue的ref和reactive函数
import { useRouter } from 'vue-router'; // 引入Vue Router的useRouter函数
import { ElMessage } from 'element-plus'; // 引入Element Plus的消息组件
import { User, Lock, Message } from '@element-plus/icons-vue'; // 引入Element Plus的图标
import type { FormInstance } from 'element-plus'; // 引入Element Plus的FormInstance类型
import api from '@/api';

// 使用 Vue Router
const router = useRouter();
// 表单引用
const formRef = ref<FormInstance>();
// 加载状态
const loading = ref(false);

// 表单数据
const formData = reactive({
  username: '', // 用户名
  email: '', // 邮箱
  password: '', // 密码
  confirmPassword: '' // 确认密码
});

// 确认密码验证函数
const validatePass2 = (_: any, value: string, callback: Function) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== formData.password) {
    callback(new Error('两次输入密码不一致!'));
  } else {
    callback();
  }
};

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }, // 用户名必填规则
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }, // 用户名长度规则
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' }, // 邮箱必填规则
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }, // 邮箱格式规则
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }, // 密码必填规则
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }, // 密码长度规则
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' }, // 确认密码必填规则
    { validator: validatePass2, trigger: 'blur' }, // 确认密码一致性验证规则
  ],
};

// 表单提交处理函数
const handleSubmit = async () => {
  if (!formRef.value) return; // 如果表单引用不存在，直接返回
  
  try {
    await formRef.value.validate(); // 使用 formRef.value.validate() 验证表单数据是否满足预设的验证规则
    loading.value = true; // 设置 loading 状态为 true，可用于显示加载中的动画和禁用提交按钮
    
    const { username, email, password } = formData;
    await api.auth.register({ username, email, password }); // 调用注册API
    
    ElMessage.success('注册成功，请登录'); // 显示成功消息
    router.push('/login'); // 跳转到登录页面
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '注册失败'); // 显示错误消息
  } finally {
    loading.value = false; // 设置加载状态为false
  }
};
// 跳转到登录页面
const goToRegister = () => {
  router.push('/login');
};
</script>

<style scoped>
/* 注册页面样式 */
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.register-card {
  width: 400px;
}

.submit-btn {
  width: 100%;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
}

.form-footer a {
  color: #409EFF;
  text-decoration: none;
}

.form-footer a:hover {
  color: #66b1ff;
}
</style>