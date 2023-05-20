import React, { Component } from "react";
import { connect } from "react-redux";
import { Router, Switch, Route, Link } from "react-router-dom";

// import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

import Login from "./components/login.component";
import Profile from "./components/profile.component";
import ReminderList from "./components/reminderlist.component";
import Documents from "./components/documents.component";

import { logout } from "./actions/auth";
import { clearMessage } from "./actions/message";

import UserService from "./services/user.service";


import { history } from './helpers/history';

// import AuthVerify from "./common/auth-verify";
import EventBus from "./common/EventBus";

import AppTitle from "./assets/svg/apptitle.js";
import ProfileIcon from "./assets/svg/profileicon.js";
import LogoutIcon from "./assets/svg/logout.js";
import GlobalAttachIcon from "./assets/svg/globalattach.js";

class App extends Component {
  constructor(props) {
    super(props);
    this.logOut = this.logOut.bind(this);

    this.state = {
      currentUser: undefined,
    };

    history.listen((location) => {
      props.dispatch(clearMessage()); // clear message when changing location
    });
  }

  componentDidMount() {
    const user = this.props.user;

    if (user) {
      this.setState({
        currentUser: user,
      });
    }

    EventBus.on("logout", () => {
      this.logOut();
    });
  }

  componentWillUnmount() {
    EventBus.remove("logout");
  }

  logOut() {
    this.props.dispatch(logout());
    this.setState({
      currentUser: undefined,
    });
    UserService.logout().then(
      response => {
        document.getElementById('headerButtons').style.display = "none";
        history.push("/login");
      },
      error => {
        document.getElementById('headerButtons').style.display = "none";
        history.push("/login");
      }
    );
  }

  // showHeaderButtons() {
  //   document.getElementById('headerButtons')
  // }

  render() {
    //const { currentUser } = this.state;
    // if(currentUser && window.location.pathname === "/login") {
    //   history.push("/reminders");
    // }
    return (
      <Router history={history}>
        <div>
          <div style={styles.header}>
            <Link to={"/reminders"}>
              <AppTitle />
            </Link>
            <div id="headerButtons" style={styles.headerButtons}>
              <Link to={"/documents"} style={styles.iconLogout}>
                <GlobalAttachIcon />
              </Link>
              <Link to={"/user"} style={styles.iconLogout} >
                <ProfileIcon />
              </Link>
              <div onClick={this.logOut} style={styles.iconLogout}>
                <LogoutIcon style={styles.iconLogout}/>
              </div>
            </div>
          </div>
          <div className="container mt-3" style={styles.mainContainer}>
            <Switch>
              <Route exact path="/login" component={Login} />
              <Route exact path="/reminders" component={ReminderList} />
              <Route exact path="/documents" component={Documents} />
              <Route exact path="/user" component={Profile} />
            </Switch>
          </div>
          {/* <AuthVerify logOut={this.logOut}/> */}
        </div>
      </Router>
    );
  }
}

function mapStateToProps(state) {
  const { user } = state.auth;
  return {
    user,
  };
}
const styles = {
  header: {
    // overflow: hidde
    maxHeight: 30,
    margin: 20,
    display: "flex",
    justifyContent: "space-between"
  },
  headerButtons: {
    display: "none",
    width: "50%"
  },
  iconLogout: {
    marginRight: "2vw",
    display: "inline",
    height: "50px",
  },
  mainContainer: {
    marginTop: "5vh"
  }
}
export default connect(mapStateToProps)(App);
