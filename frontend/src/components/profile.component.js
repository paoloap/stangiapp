import React, { Component } from "react";

import UserService from "../services/user.service";
import EventBus from "../common/EventBus";

import "../assets/css/spinner.css";

export default class BoardUser extends Component {
  constructor(props) {
    super(props);

    this.state = {
      content: ""
    };
  }

  componentDidMount() {
    UserService.getProfile().then(
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
    var user_profile = [];
    var res = this.state.content;
    if (res === "" || typeof res === "number" || res === "unknown") {
      return (
        <div className="loader-container">
      	  <div className="spinner"></div>
        </div>
      )
    } else {
      this.state.content.profile.forEach(
        profile_elem => {
          var value;
          if (profile_elem.label === "Indirizzo") {
            value = profile_elem.value.street + ", " + profile_elem.value.num + ", " + profile_elem.value.code + ", " + profile_elem.value.locality + " (" + profile_elem.value.state + ")";
          } else {
            value = profile_elem.value;
          }
          user_profile.push(
            <div style={styles.profileElement} key={profile_elem.label}>
              <div style={styles.label}>{profile_elem.label}</div>
              <div style={styles.value}>{value}</div>
            </div>
          )
        }
      );
      return (
        <div style={styles.container}>
          {user_profile}
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
    profileElement : {
      width: perc * 80,
      height: perc * 40,
      borderRadius: perc * 1,
      display: "flex",
      flexDirection: "column",
      gap: perc * 10,
      position: "relative",
      backgroundColor: "rgba(238,172,190,0.5)",
      border: 0,
      transition: "0.3s all",
      textAlign: "center",
    },
    label : {
      fontFamily: "Staatliches-Regular",
      fontSize: perc * 7,
    },
    value : {
      fontFamily: "URWGothic-Book",
      fontSize: perc * 5,
    },
  }
}
