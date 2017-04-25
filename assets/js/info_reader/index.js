import React from 'react';
import ReactDOM from 'react-dom';
import { Pagination, Card, Button, Icon, Row, Col, Radio, Switch, Input } from 'antd';
import 'antd/dist/antd.css';  // or 'antd/dist/antd.less'
const RadioGroup = Radio.Group;
const radioStyle = {
  display: 'block',
  height: '30px',
  lineHeight: '30px',
};
const Search = Input.Search;

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
    if (!this.props.info_item.is_read){
      var mark_as_read_button = <Button type="primary" style={{ marginRight:10 }} onClick={this.markAsRead} >Mark as Read<Icon type="check" /></Button>
    }else{
      var mark_as_read_button = <Icon type="check" />
    }
    var create_read_button = <Button type="primary" style={{ marginRight:10 }}><a href={this.props.info_item.create_read_url} target="_blank">Create Read<Icon type="plus" /></a></Button>

    var content = '';
    if (this.props.info_item.content){
      var content = <div dangerouslySetInnerHTML={{__html: this.props.info_item.content}}></div>;
    }

    return (
      <Card title={<a href={this.props.info_item.url} target="_blank">{this.props.info_item.title} <Icon type="link" /></a>} extra={this.props.info_item.source_name} style={{ margin:'12px 0' }}>
        <p>
          {star_button}
          {create_read_button}
          {mark_as_read_button}
        </p>
        <p style={{marginTop:10}}><img src={this.props.info_item.author_avatar} /> {this.props.info_item.author_name}</p>
        {content}
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
    this.setState({info_source: e.target.value, page:1}, function(){
      this.loadInfo();
    })
  },
  onlyStarItems: function(checked){
    var show_starred_items=false;
    if (checked){
      show_starred_items=true;
    }else{
      show_starred_items=null;
    }
    this.setState({show_starred_items: show_starred_items, page:1}, function(){
      this.loadInfo();
    })
  },
  search: function(value){
    this.setState({search_title: value, page:1}, function(){
      this.loadInfo()
    })
  },
  showReadItems: function(checked){
    var show_read_items=false;
    if (checked){
      show_read_items=null;
    }
    this.setState({show_read_items: show_read_items, page:1}, function(){
      this.loadInfo();
    })
  },
  loadInfo: function() {
    $.ajax({
      url: this.props.url,
      data: {
        page: this.state.page,
        title__contains: this.state.search_title,
        starred: this.state.show_starred_items,
        is_read: this.state.show_read_items,
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
      search_title: '',
      show_starred_items: null,
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
            <Switch checkedChildren={'显示已读'} unCheckedChildren={'隐藏已读'} onChange={this.showReadItems}
              style={{marginTop:'10px', width:'100px'}}
            />
            <br />
            <Switch checkedChildren={'仅收藏'} unCheckedChildren={'全部'} onChange={this.onlyStarItems}
              style={{marginTop:'10px', width:'100px'}}
            />
            <Search placeholder="Search title" onSearch={this.search} style={{marginTop:'10px', width:'200px'}} />
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
