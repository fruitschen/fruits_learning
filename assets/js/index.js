import React from 'react';
import ReactDOM from 'react-dom';


var InfoItem = React.createClass({
  render: function() {
    return (
      <div className="info_item">
        <h2 className="infoTitle">
          {this.props.info_item.title}
        </h2>
        <p><a href={this.props.info_item.url}>Go to info</a></p>
        <p><a href={this.props.info_item.absolute_url}>Info Details</a></p>
        <p><a href={this.props.info_item.mark_as_read}>Mark as read</a></p>
      </div>
    );
  }
});

var InfoItemBox = React.createClass({
  loadInfoItemsFromServer: function() {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({
          info_items: data.results,
          previous: data.previous,
          next: data.next,
        });
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
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
    this.loadInfoItemsFromServer();
  },
  render: function() {
    return (
      <div className="infoBox">
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
