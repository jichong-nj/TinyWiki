/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare namespace wps {
  namespace Api {
    class OAApi {
      constructor()
      Event: {
        Load: string
      }
    }
    function oa(): OAApi
  }
}
