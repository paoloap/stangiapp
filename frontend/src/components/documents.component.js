import React, { Component } from "react";

import UserService from "../services/user.service";
import EventBus from "../common/EventBus";
import AttachedDoc from '../assets/svg/attacheddoc';
import "../assets/css/spinner.css";

export default class Documents extends Component {
  constructor(props) {
    super(props);

    this.state = {
      content: ""
    };
  }

  componentDidMount() {
    UserService.getGlobalAttachments().then(
      response => {
        this.setState({
          content: response.data
        });
      },
      error => {
        var content = (
          error.response && ( error.response.status || error.response.data.detail )
        ) || "unknown";
        this.setState({ content: content });
        if (
          !error.response ||
          (error.response && [401, 403].includes(error.response.status))
	) {
          EventBus.dispatch("logout");
        }
      }
    );
  }

  componentDidUpdate() {
    document.getElementById('headerButtons').style.display = "block";
  }

  render() {
    var styles = Style(window.innerWidth);
    var docs_list = [];
    var res = this.state.content;
    if (res === "" || typeof res === "number" || res === "unknown") {
      return (
        <div className="loader-container">
      	  <div className="spinner"></div>
        </div>
      )
    } else {
      this.state.content.file_list.forEach(element => {
        docs_list.push(
          <div style={styles.downloadItem}>
            <a style={styles.noDecoration} href={element.link}>
              <AttachedDoc height={styles.myAttaches.height} />
              <span style={styles.downloadName}>{element.name}</span>
            </a>
          </div>
        )
      });
      return (
        <div style={styles.container}>
	  <div style={styles.title}>Documentazione generale</div>
          {docs_list}
        </div>
      );
    }
  }
}
function Style(windowWidth) {
  const perc = windowWidth / 100;
  return {
    container : {
      display: "flex",
      flexDirection: "column",
      gap: perc * 5,
      // justifyContent: "space-between",
      position: "absolute",
      width: perc * 80,
      top: perc * 30,
      left: perc * 10,
      textAlign: "center",
    },
    title: {
      fontSize: perc * 8,
      fontFamily: "Staatliches-Regular",
      color: "#7FE4CC",
    },
    myAttaches: {
      position: "relative",
      display: "flex",
      justifyContent: "space-between",
      height: perc * 13,
      top: perc * -25,
      left: perc * 5,
      width: perc * 80,
    },
    downloadName: {
      position: "relative",
      top: perc * -5,
      left: perc * 3,
      fontFamily: "URWGothic-Book",
      fontSize: perc * 3.5,
    },
    downloadItem: {
      display: "flex",
      position: "relative",
      left: perc * 5,
      overflow: "hidden",
      fontFamily: "URWGothic-Book",
      fontSize: perc * 3.5,
      color: "#FFFFFF"
    },
    noDecoration: {
      textDecoration: "none",
      color: "black",
    }
  }
}
