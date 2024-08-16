import LogicFlow, {
  GraphModel, // 图形模型，用于管理和操作图形
  CircleNodeModel,
  CircleNode,
  h,
  RectNode,
  RectNodeModel,
  PolygonNode,
  PolygonNodeModel,
} from '@logicflow/core';

import { nodeProperty } from '../type';

export default function RegisteNode(lf: LogicFlow) {
  class ApplyNodeModel extends CircleNodeModel {
  }
  lf.register({
    type: 'apply',
    view: CircleNode,
    model: ApplyNodeModel,
  })

  class ApproverNode extends RectNode {
    static extendKey = 'UserTaskNode';
    getLabelShape() {
      const {
        x,
        y,
        width,
        height,
        properties,
      } = this.props.model;
      const { labelColor, approveTypeLabel } = properties as nodeProperty;
      return h(
        'text',
        {
          fill: labelColor,
          fontSize: 12,
          x: x - width / 2 + 5,
          y: y - height / 2 + 15,
          width: 50,
          height: 25
        },
        approveTypeLabel,
      );
    }

    getShape() {
      const {
        x,
        y,
        width,
        height,
        radius,
      } = this.props.model;
      const style = this.props.model.getNodeStyle();
      return h(
        'g',
        {
        },
        [
          h(
            'rect',
            {
              ...style,
              x: x - width / 2,
              y: y - height / 2,
              rx: radius,
              ry: radius,
              width,
              height,
            },
          ),
          this.getLabelShape(),
        ],
      );
    }
  }

  
  class ApproverModel extends RectNodeModel { 
    constructor(data: any, graphModel: GraphModel) {
      super(data, graphModel);
      this.properties = {
        labelColor: '#000000',
        approveTypeLabel: '',
        approveType: ''
      }
    }
  }

  lf.register({
    type: 'approver',
    view: ApproverNode,
    model: ApproverModel,
  })

  class JugementModel extends PolygonNodeModel { 
    constructor(data: any, graphModel: GraphModel) {
      super(data, graphModel);
      this.points= [
        [35, 0],
        [70, 35],
        [35, 70],
        [0, 35],
      ];
      this.properties = {
        api: '',
      }
    }
  }
  lf.register({
    type: 'jugement',
    view: PolygonNode,
    model: JugementModel,
  });

  class FinshNodeModel extends CircleNodeModel {
  }
  lf.register({
    type: 'finsh',
    view: CircleNode,
    model: FinshNodeModel,
  })
}
