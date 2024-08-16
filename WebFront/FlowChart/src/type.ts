// Purpose: This TypeScript file generally defines types and interfaces used in the application. It helps TypeScript provide static type checking and code completion features. You might define component props types, state types, etc., in this file.
export type HtmlNodeConfig = {
    type: string,
    label: string,
    style: {
      width: string,
      height: string,
      borderRadius?: string,
      border: string,
      transform?: string,
    }
  }
  export type IApproveUser = {
    label: string,
    value: string,
  }
  export type nodeProperty = {
    labelColor: string,
    approveTypeLabel: string,
    approveType: string,
  }