import React from 'react';
import LogicFlow from '@logicflow/core';
import { HtmlNodeConfig } from '../type';

const approveNodes = [
    {
      type: 'apply',
      label: '申请',
      style: {
        width: '30px',
        height: '30px',
        borderRadius: '15px',
        border: '2px solid #FF6347',
      },
      property: {
        username: '',
        time: '',
        startTime: '',
        endTime: '',
  
      }
    },
    {
      type: 'approver',
      label: '审批',
      style: {
        width: '50px',
        height: '40px',
        borderRadius: '4px',
        border: '2px solid #3CB371',
      }
    },
    {
      type: 'jugement',
      label: '判断',
      style: {
        width: '30px',
        height: '30px',
        border: '2px solid #6495ED',
        transform: 'rotate(45deg)',
      }
    },
    {
      type: 'finsh',
      label: '结束',
      style: {
        width: '30px',
        height: '30px',
        borderRadius: '15px',
        border: '2px solid #FF6347',
      }
    },
  ];
export default function NodePanel(lf: LogicFlow) {
  // 拖拽创建
  const dragNode = (item: HtmlNodeConfig) => { 
    lf.dnd.startDrag({
      type: item.type,
      text: item.label
    })
  }
  // 节点菜单
  const getNodePanel = (): JSX.Element[]  => { 
    const nodeList: JSX.Element[] = [];
    approveNodes.forEach((item, key) => { 
      nodeList.push(
        <div
          className={`approve-node node-${item.type}`}
          key={key}
        >
          <div
            className="node-shape"
            style={{ ...item.style }}
            onMouseDown={() => dragNode(item)}
          ></div>
          <div className="node-label">{item.label}</div>
        </div>
      )
    })
    return nodeList;
  }
  return getNodePanel()
}