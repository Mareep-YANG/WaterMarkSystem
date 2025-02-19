<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>个人信息</h3>
            </div>
          </template>

          <el-descriptions border>
            <el-descriptions-item label="用户名">
              {{ user?.username }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ user?.email }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="user?.is_active ? 'success' : 'danger'">
                {{ user?.is_active ? '正常' : '禁用' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>API密钥管理</h3>
              <el-button
                type="primary"
                size="small"
                @click="handleCreateApiKey"
              >
                创建密钥
              </el-button>
            </div>
          </template>

          <el-alert
            v-if="newApiKey"
            type="success"
            :closable="false"
            class="mb-20"
          >
            <template #default>
              <p>请保存您的新API密钥，此密钥仅显示一次：</p>
              <el-input v-model="newApiKey" readonly>
                <template #append>
                  <el-button @click="copyApiKey">复制</el-button>
                </template>
              </el-input>
            </template>
          </el-alert>

          <el-table :data="apiKeys" stripe style="width: 100%">
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="created_at" label="创建时间">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button
                  type="danger"
                  size="small"
                  @click="handleRevokeApiKey(row.id)"
                >
                  撤销
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog
      v-model="dialogVisible"
      title="创建API密钥"
      width="400px"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="top"
      >
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            placeholder="请输入密钥描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitApiKey">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance } from 'element-plus';
import { useUserStore } from '@/stores';
import api from '@/api';

interface ApiKey {
  id: string;
  description: string;
  created_at: string;
}

const userStore = useUserStore();
const user = computed(() => userStore.currentUser);

const apiKeys = ref<ApiKey[]>([]);
const newApiKey = ref('');
const dialogVisible = ref(false);
const formRef = ref<FormInstance>();

const formData = reactive({
  description: '',
});

const rules = {
  description: [
    { required: true, message: '请输入密钥描述', trigger: 'blur' },
    { min: 3, message: '描述至少3个字符', trigger: 'blur' },
  ],
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleString();
};

const fetchApiKeys = async () => {
  try {
    const response = await api.auth.getApiKeys();
    apiKeys.value = response;
  } catch (error) {
    ElMessage.error('获取API密钥列表失败');
  }
};

const handleCreateApiKey = () => {
  formData.description = '';
  dialogVisible.value = true;
};

const submitApiKey = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    const response = await api.auth.createApiKey(formData.description);
    newApiKey.value = response.key;
    dialogVisible.value = false;
    await fetchApiKeys();
    ElMessage.success('API密钥创建成功');
  } catch (error: any) {
    ElMessage.error(error.message || 'API密钥创建失败');
  }
};

const handleRevokeApiKey = async (id: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要撤销此API密钥吗？此操作不可恢复',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    await api.auth.revokeApiKey(id);
    await fetchApiKeys();
    ElMessage.success('API密钥已撤销');
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('API密钥撤销失败');
    }
  }
};

const copyApiKey = () => {
  navigator.clipboard.writeText(newApiKey.value)
    .then(() => {
      ElMessage.success('API密钥已复制到剪贴板');
    })
    .catch(() => {
      ElMessage.error('复制失败，请手动复制');
    });
};

onMounted(async () => {
  await fetchApiKeys();
});
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mb-20 {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>