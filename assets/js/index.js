import React from 'react';
import ReactDOM from 'react-dom';
import { Pagination, Card, Button, Icon, Row, Col, Radio } from 'antd';
import 'antd/dist/antd.css';  // or 'antd/dist/antd.less'
const RadioGroup = Radio.Group;

var InfoItem = React.createClass({
  getInitialState: function() {
    return {
      read: this.props.info_item.read_at,
    };
  },

  markAsRead: function() {
    var url = this.props.info_item.mark_as_read;
    $.ajax({
      type: 'POST',
      dataType: 'json',
      url: url,
      data: {},
      success: function(data){
        this.setState({'read': true})
      }.bind(this)
    });
  },

  render: function() {
    if (this.state.read){
      return(
        <Card title={this.props.info_item.title} extra={this.props.info_item.source_name}>
          <Icon type="check" />
        </Card>
      )
    }
    var show_mark_as_read = ! this.state.read;
    if (show_mark_as_read){
      var mark_button = <Button onClick={this.markAsRead} >Mark as Read</Button>
    }else{
      var mark_button = null
    }
    return (
      <Card title={this.props.info_item.title} extra={this.props.info_item.source_name}>
        <p>
          <Button><a href={this.props.info_item.url} target="_blank">Go to info</a></Button>
          <Button><a href={this.props.info_item.absolute_url} target="_blank">Info Details</a></Button>
          {mark_button}
        </p>
      </Card>
    );
  }
});


var InfoItemList = React.createClass({
  render: function() {
    var infoNodes = this.props.info_items.map(function(info_item) {
      return (
        <InfoItem info_item={info_item} key={info_item.id}></InfoItem>
      );
    });
    return (
      <div className="infoList">
        {infoNodes}
      </div>
    );
  }
});


var InfoSourceList = React.createClass({
  getInitialState: function() {
    return {
      value: 1,
    };
  },
  render: function() {
    var infoSourceNodes = this.props.info_sources.map(function(info_source) {
      return (
        <Radio value={info_source.id} key={info_source.id}>{info_source.name}</Radio>
      );
    });
    return (
      <div className="infoSourceList">
        <RadioGroup onChange={this.props.onChange} defaultValue={this.state.value}>
          {infoSourceNodes}
        </RadioGroup>
      </div>
    );
  }
});


var InfoReader = React.createClass({
  changePage: function(page, pageSize){
    this.setState({page: page}, function(){
      this.loadInfo();
    })
  },
  selectSource: function(e){
    this.setState({info_source: e.target.value}, function(){
      this.loadInfo();
    })
  },
  loadInfo: function() {
    $.ajax({
      url: this.props.url,
      data: {
        page: this.state.page,
        is_read: false,
        info_source: this.state.info_source
      },
      dataType: 'json',
      cache: false,
      success: function(data) {
        let count = data.count;
        this.setState({
          info_items: data.results,
          previous: data.previous,
          next: data.next,
          total: data.count,
        });
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(url, status, err.toString());
      }.bind(this)
    });
  },
  loadSources: function(){
    $.ajax({
      url: '/api/info-source/',
      data: {},
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({
          info_sources: data.results,
        });
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(url, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {
      page: 1,
      info_items: [],
      info_sources: [],
      previous: null,
      next: null,
      info_source: null,
      show_read_items: false
    };
  },
  componentDidMount: function() {
    this.loadInfo();
    this.loadSources();
  },
  render: function() {
    return (
      <div className="infoReader">
        <Row gutter={16}>
          <Col className="gutter-row" span={16}>
            <Pagination defaultCurrent={this.state.page} total={this.state.total} pageSize={50} onChange={this.changePage} current={this.state.page} />
            <InfoItemList info_items={this.state.info_items} />
          </Col>
          <Col className="gutter-row" span={8}>
            <InfoSourceList info_sources={this.state.info_sources} onChange={this.selectSource} />
          </Col>
        </Row>
      </div>
    );
  }
});


ReactDOM.render(
  <InfoReader url="/api/info/" />,
  document.getElementById('react-app')
);
