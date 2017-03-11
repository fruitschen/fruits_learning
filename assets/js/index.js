import React from 'react';
import ReactDOM from 'react-dom';
import { Pagination, Card, Button, Icon } from 'antd';
import 'antd/dist/antd.css';  // or 'antd/dist/antd.less'

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
        <Card title={this.props.info_item.title} style={{ width: 800 }}>
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
      <Card title={this.props.info_item.title} style={{ width: 800 }}>
        <p>
          <Button><a href={this.props.info_item.url} target="_blank">Go to info</a></Button>
          <Button><a href={this.props.info_item.absolute_url} target="_blank">Info Details</a></Button>
          {mark_button}
        </p>
      </Card>
    );
  }
});

var InfoItemBox = React.createClass({
  changePage: function(page, pageSize){
    this.loadInfo(page);
  },
  loadInfo: function(page) {
    $.ajax({
      url: this.props.url,
      data: {
        page: (page || 1),
        is_read: false
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
  getInitialState: function() {
    return {
      info_items: [],
      previous: null,
      next: null,
      show_read_items: false
    };
  },
  componentDidMount: function() {
    this.loadInfo();
  },
  render: function() {
    return (
      <div className="infoBox">
        <Pagination defaultCurrent={1} total={this.state.total} pageSize={50} onChange={this.changePage} />
        <InfoItemList info_items={this.state.info_items} />
      </div>
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

ReactDOM.render(
  <InfoItemBox url="/api/info/" />,
  document.getElementById('react-app')
);
