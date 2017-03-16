import React from 'react';
import ReactDOM from 'react-dom';
import { Pagination, Card, Button, Icon, Row, Col, Radio, Switch } from 'antd';
import 'antd/dist/antd.css';  // or 'antd/dist/antd.less'
const RadioGroup = Radio.Group;
const radioStyle = {
  display: 'block',
  height: '30px',
  lineHeight: '30px',
};

var Entry = React.createClass({
  getInitialState: function() {
    return {
      starred: this.props.entry.starred,
    };
  },

  markAsRead: function() {
    var url = this.props.entry.mark_as_read;
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
        <Icon type="check" />
      )
    }

    if (!this.props.entry.is_read){
      var mark_as_read_button = <Button type="primary" style={{ marginRight:10 }} onClick={this.markAsRead} >Mark as Read<Icon type="check" /></Button>
    }else{
      var mark_as_read_button = <Icon type="check" />
    }

    var content = '';
    if (this.props.entry.description){
      var content = <div dangerouslySetInnerHTML={{__html: this.props.entry.description}}></div>;
    }

    return (
      <Card title={<a href={this.props.entry.link} target="_blank">{this.props.entry.title} <Icon type="link" /></a>} extra={this.props.entry.feed_name} style={{ margin:'12px 0' }}>
        <p>
          {mark_as_read_button}
        </p>
        {content}
      </Card>
    );
  }
});


var EntryList = React.createClass({
  render: function() {
    var entryNodes = this.props.entries.map(function(entry) {
      return (
        <Entry entry={entry} key={entry.id}></Entry>
      );
    });
    return (
      <div className="entryList">
        {entryNodes}
      </div>
    );
  }
});


var FeedList = React.createClass({
  getInitialState: function() {
    return {
      value: null,
    };
  },
  render: function() {
    var feedNodes = this.props.feeds.map(function(feed) {
      return (
        <Radio style={radioStyle}  value={feed.id} key={feed.id}>{feed.title}</Radio>
      );
    });
    return (
      <div className="feedList">
        <RadioGroup onChange={this.props.onChange} defaultValue={this.state.value}>
          <Radio style={radioStyle}  value={null} key={0}>全部</Radio>
          {feedNodes}
        </RadioGroup>
      </div>
    );
  }
});


var FeedReader = React.createClass({
  changePage: function(page, pageSize){
    this.setState({page: page}, function(){
      this.loadEntryData();
    })
  },
  selectFeed: function(e){
    this.setState({feed: e.target.value, page:1}, function(){
      this.loadEntryData();
    })
  },
  showReadItems: function(checked){
    var show_read_items=false;
    if (checked){
      show_read_items=null;
    }
    this.setState({show_read_items: show_read_items, page:1}, function(){
      this.loadEntryData();
    })
  },
  loadEntryData: function() {
    $.ajax({
      url: this.props.url,
      data: {
        page: this.state.page,
        read_flag: this.state.show_read_items,
        feed: this.state.feed
      },
      dataType: 'json',
      cache: false,
      success: function(data) {
        let count = data.count;
        this.setState({
          entries: data.results,
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
  loadFeeds: function(){
    $.ajax({
      url: '/api/feed/',
      data: {},
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({
          feeds: data.results,
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
      entries: [],
      feeds: [],
      previous: null,
      next: null,
      feed: null,
      show_read_items: false
    };
  },
  componentDidMount: function() {
    this.loadEntryData();
    this.loadFeeds();
  },
  render: function() {
    return (
      <div className="FeedReader" style={{ margin:'12px 48px' }}>
        <h1>Feed Reader</h1>
        <Row gutter={16}>
          <Col className="gutter-row" span={4}>
            <FeedList feeds={this.state.feeds} onChange={this.selectFeed} />
            <Switch checkedChildren={'显示已读'} unCheckedChildren={'隐藏已读'} onChange={this.showReadItems}
              style={{marginTop:'10px'}}
            />
          </Col>
          <Col className="gutter-row" span={20}>
            <Pagination defaultCurrent={this.state.page} total={this.state.total} pageSize={50} onChange={this.changePage} current={this.state.page} />
            <EntryList entries={this.state.entries} />
          </Col>
        </Row>
      </div>
    );
  }
});


ReactDOM.render(
  <FeedReader url="/api/entry/" />,
  document.getElementById('react-app')
);
