declare module 'element-plus/dist/locale/zh-cn.mjs' {
  const zhCn: {
    name: string;
    el: {
      [key: string]: any;
    };
  };
  export default zhCn;
}

declare module 'element-plus/dist/locale/*' {
  const locale: {
    name: string;
    el: {
      [key: string]: any;
    };
  };
  export default locale;
}