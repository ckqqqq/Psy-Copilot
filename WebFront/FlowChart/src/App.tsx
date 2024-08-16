
import LogicFlow from '@logicflow/core';
import '@logicflow/core/dist/index.css';
import { useEffect, useRef } from 'react';
import './index.css'; // 确保你有一个 CSS 文件来设置高度
import RegisteNode from './components/registerNode';
import NodePanel from './components/NodePanel';
import { useState } from 'react';

// DndPanel
import { DndPanel, SelectionSelect } from "@logicflow/extension";
// import "@logicflow/core/dist/style/index.css"; // 2.0版本前的引入方式
import "@logicflow/extension/lib/style/index.css";

import {flowChartData} from "./data/GraphData"

import {styleFlowChart,SideBarConfig} from "./data/ConfigData"

import PropertyPanel from './components/property';



function App() {
  
  const refContainer = useRef() as React.MutableRefObject<HTMLDivElement>;
  
  const [lf, setLf] = useState({} as LogicFlow);
  const [nodeData,setNodeData] = useState<any>(undefined);
  
  useEffect(() => {
   
    const lf = new LogicFlow({
      stopScrollGraph: true,
      stopZoomGraph: true,
      container: refContainer.current,
      style:styleFlowChart,// 自定义样式
      grid: true, // 开启网格
      plugins: [DndPanel, SelectionSelect],
      keyboard: {
        enabled: true
      },
    });
    // lf.render(data);
    setLf(lf);
    RegisteNode(lf);
     // 使用类型断言 设置侧边栏
     const dndPanel = lf.extension.dndPanel as any;
     if (dndPanel && typeof dndPanel.setPatternItems === 'function') {
       dndPanel.setPatternItems(SideBarConfig);
     }

    lf.render(flowChartData);
    lf.translateCenter();
    initEvent(lf);
  }, []);
  //  一个函数，将LogicFlow实例作为参数，并为其添加一个点击事件监听器。
  const initEvent = (lf: LogicFlow) => { 
    lf.on('element:click', ({ data }) => {
      setNodeData(data);
      console.log(JSON.stringify(lf.getGraphData()));
    });
  }
   // 更新属性，根据id和data更新节点或边的属性
   const updateProperty = (id: string, data: any) => {
    const node = lf.graphModel.nodesMap[id];
    const edge = lf.graphModel.edgesMap[id];
    if (node) {
      node.model.setProperties(Object.assign(node.model.properties, data));
    } else if (edge) {
      edge.model.setProperties(Object.assign(edge.model.properties, data));
    }
  }
  // 隐藏属性面板
  const hidePropertyPanel = () => { 
    setNodeData(undefined);
  }
  //  设置侧边栏
  
  return (
    <div className="App" id="container" ref={refContainer} >
      <div className="node-panel">
        {/* { NodePanel(lf) } */}
      </div>
      { nodeData ? 
      <div className="property-panel">
        {PropertyPanel(nodeData, updateProperty, hidePropertyPanel)}
      </div> : ''}
    </div>
    
  );
}
// 条件渲染：{ nodeData ? ... : ''}，表示只有当nodeData存在时，才会渲染属性面板。

// 类名：property-panel，可能用于应用样式或JavaScript选择器。

// 内容：{PropertyPanel(nodeData, updateProperty, hidePropertyPanel)}，这是一个React组件或函数调用，传入了nodeData、updateProperty和hidePropertyPanel作为参数，用于渲染属性面板的内容。

export default App;
