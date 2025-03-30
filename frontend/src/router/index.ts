import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'; // 引入Vue Router的相关函数和类型
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'), // 懒加载Home组件
    meta: { requiresAuth: true } // 需要认证的页面
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'), // 懒加载Register组件
    meta: { guest: true } // 游客页面
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'), // 懒加载Login组件
    meta: { guest: true } // 游客页面
  },
  {
    path: '/watermark',
    name: 'Watermark',
    component: () => import('@/views/Watermark.vue'), // 懒加载Watermark组件
    meta: { requiresAuth: true } // 需要认证的页面
  },
  {
    path: '/evaluate',
    name: 'Evaluate',
    component: () => import('@/views/Evaluate.vue'), // 懒加载Evaluate组件
    meta: { requiresAuth: true } // 需要认证的页面
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'), // 懒加载Profile组件
    meta: { requiresAuth: true } // 需要认证的页面
  }
];

const router = createRouter({
  history: createWebHistory(), // 使用HTML5历史模式
  routes // 路由配置
});

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token'); // 从本地存储获取token
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 需要认证的页面
    if (!token) {
      next({
        path: '/login',
        query: { redirect: to.fullPath } // 重定向到登录页面，并传递重定向地址
      });
    } else {
      next(); // 已认证，继续导航
    }
  } else if (to.matched.some(record => record.meta.guest)) {
    // 游客页面
    if (token) {
      next('/'); // 已登录，重定向到首页
    } else {
      next(); // 未登录，继续导航
    }
  } else {
    next(); // 无需认证，继续导航
  }
});

export default router; // 导出路由实例