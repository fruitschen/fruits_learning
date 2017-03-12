import React from 'react';
import ReactDOM from 'react-dom';
import { Pagination, Card, Button, Icon, Row, Col, Radio } from 'antd';
import 'antd/dist/antd.css';  // or 'antd/dist/antd.less'
const RadioGroup = Radio.Group;

var InfoItem = React.createClass({
  getInitialState: function() {
    return {
      starred: this.props.info_item.starred,
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

  star: function() {
    var url = this.props.info_item.star_url;
    $.ajax({
      type: 'POST',
      dataType: 'json',
      url: url,
      data: {},
      success: function(data){
        this.setState({'starred': true})
      }.bind(this)
    });
  },

  unstar: function() {
    var url = this.props.info_item.unstar_url;
    $.ajax({
      type: 'POST',
      dataType: 'json',
      url: url,
      data: {},
      success: function(data){
        this.setState({'starred': false})
      }.bind(this)
    });
  },

  render: function() {
    if (this.state.read){
      return(
        <Icon type="check" />
      )
    }
    if (!this.state.starred){
      var star_button = <Button style={{ marginRight:10 }} type="primary" onClick={this.star} >Star<Icon type="star-o" /></Button>
    }else{
      var star_button = <Button style={{ marginRight:10 }} type="primary" onClick={this.unstar} >Star<Icon type="star" /></Button>
    }
    return (
      <Card title={<a href={this.props.info_item.url} target="_blank">{this.props.info_item.title} <Icon type="link" /></a>} extra={this.props.info_item.source_name} style={{ margin:'12px 0' }}>
        <p>
          {star_button}
          <Button type="primary" style={{ marginRight:10 }} onClick={this.markAsRead} >Mark as Read<Icon type="check" /></Button>
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
      value: null,
    };
  },
  render: function() {
    const radioStyle = {
      display: 'block',
      height: '30px',
      lineHeight: '30px',
    };
    var infoSourceNodes = this.props.info_sources.map(function(info_source) {
      return (
        <Radio style={radioStyle}  value={info_source.id} key={info_source.id}>{info_source.name}</Radio>
      );
    });
    return (
      <div className="infoSourceList">
        <RadioGroup onChange={this.props.onChange} defaultValue={this.state.value}>
          <Radio style={radioStyle}  value={null} key={0}>全部</Radio>
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
      <div className="infoReader" style={{ margin:'12px 48px' }}>
        <h1>Info Reader</h1>
        <Row gutter={16}>
          <Col className="gutter-row" span={4}>
            <InfoSourceList info_sources={this.state.info_sources} onChange={this.selectSource} />
          </Col>
          <Col className="gutter-row" span={20}>
            <Pagination defaultCurrent={this.state.page} total={this.state.total} pageSize={50} onChange={this.changePage} current={this.state.page} />
            <InfoItemList info_items={this.state.info_items} />
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
