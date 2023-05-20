import React, { Component } from "react";

import Form from "react-validation/build/form";
import Input from "react-validation/build/input";
import CheckButton from "react-validation/build/button";

import { connect } from "react-redux";
import { login } from "../actions/auth";

const required = (value) => {
  if (!value) {
    return (
      <div className="alert alert-danger" role="alert">
        Questo campo è obbligatorio
      </div>
    );
  }
};

class Login extends Component {
  constructor(props) {
    super(props);
    this.handleLogin = this.handleLogin.bind(this);
    this.onChangeUsername = this.onChangeUsername.bind(this);
    this.onChangePassword = this.onChangePassword.bind(this);

    this.state = {
      username: "",
      password: "",
      loading: false,
    };
  }

  onChangeUsername(e) {
    this.setState({
      username: e.target.value,
    });
  }

  onChangePassword(e) {
    this.setState({
      password: e.target.value,
    });
  }

  handleLogin(e) {
    e.preventDefault();

    this.setState({
      loading: true,
    });

    this.form.validateAll();

    const { dispatch, history } = this.props;

    if (this.checkBtn.context._errors.length === 0) {
      dispatch(login(this.state.username, this.state.password))
        .then(() => {
          history.push("/reminders");
        })
        .catch(() => {
          this.setState({
            loading: false
          });
        });
    } else {
      this.setState({
        loading: false,
      });
    }
  }

  render() {
    var styles = Style(window.innerWidth);
    const { isLoggedIn, message } = this.props;

    if (isLoggedIn) {
      // return <Redirect to="/reminders" />;
      console.log("loggato")
    }

    return (
      <Form
        style={styles.loginBox}
        onSubmit={this.handleLogin}
        ref={(c) => {
          this.form = c;
        }}
      >
        <div>
          {/* <label htmlFor="username">Username</label> */}
          <Input
            style={styles.loginInput}
            type="text"
            className="form-control"
            placeholder="Nome utente"
            name="username"
            value={this.state.username}
            onChange={this.onChangeUsername}
            validations={[required]}
          />
        </div>

        <div>
          {/* <label htmlFor="password">Password</label> */}
            <Input
            style={styles.loginInput}
            type="password"
            className="form-control"
            placeholder="Password"
            name="password"
            value={this.state.password}
            onChange={this.onChangePassword}
            validations={[required]}
          />
        </div>

        <div>
          <button
            style={styles.loginButton}
            disabled={this.state.loading}
          >
            {this.state.loading && (
              <span className="spinner-border spinner-border-sm"></span>
            )}
            <span>Entra</span>
          </button>
        </div>

        {message && (
          <div>
            <div role="alert">
              {message}
            </div>
          </div>
        )}
        <CheckButton
          style={{ display: "none" }}
          ref={(c) => {
            this.checkBtn = c;
          }}
        />
      </Form>
    );
  }
}

function mapStateToProps(state) {
  const { isLoggedIn } = state.auth;
  const { message } = state.message;
  return {
    isLoggedIn,
    message
  };
}

function Style(windowWidth) {
  const perc = windowWidth / 100;
  return {
    loginBox : {
      display: "flex",
      flexDirection: "column",
      gap: perc * 10,
      // justifyContent: "space-between",
      position: "absolute",
      width: perc * 80,
      height: perc * 45,
      top: perc * 40,
      left: perc * 10,
      textAlign: "center",
    },
    loginInput : {
      width: perc * 80,
      height: perc * 10,
      borderRadius: perc * 1,
      position: "relative",
      backgroundColor: "rgba(127,228,204,0.5)",
      border: 0,
      transition: "0.3s all",
      textAlign: "center",
      fontFamily: "URWGothic-Book",
      fontSize: perc * 5,
    },
    loginButton: {
      backgroundColor: "rgba(127,228,204,1)",
      color: "white",
      fontSize: perc * 5,
      fontFamily: "Staatliches-Regular",
      padding: "10px 60px",
      borderRadius: "5px",
      margin: "10px 0px",
    }
  }
}


export default connect(mapStateToProps)(Login);
