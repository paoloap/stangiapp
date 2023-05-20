import React, { Component } from "react";

import UserService from "../services/user.service";
import EventBus from "../common/EventBus";
import Reminder from "./reminder.js"
import "../assets/css/spinner.css";

export default class ReminderList extends Component {
  constructor(props) {
    super(props);

    this.state = {
      content: "",
      //currentReminderId : qs.parse(this.props.location.search, { ignoreQueryPrefix: true }).reminder_id,
      //currentReminderPage : qs.parse(this.props.location.search, { ignoreQueryPrefix: true }).page,
      reminderContext: {
        shownStatuses: ["Attivo", "Archiviato", "Approvato"],
        showExpired : true
      },
      shownFilter: false
    };
    this.handleFilterButton = this.handleFilterButton.bind(this);
    this.checkStatusFilter = this.checkStatusFilter.bind(this);
    this.checkExpireFilter = this.checkExpireFilter.bind(this);
  }
  handleFilterButton() {
    this.setState(prevState => ({
      showFilter: !prevState.showFilter 
    }));
  }
  checkStatusFilter(event) {
    var statusName = event.target.id;
    var checked = event.target.checked;
    if(checked && !this.state.reminderContext.shownStatuses.includes(statusName)) {
      this.setState(prevState => ({
        reminderContext: {
          shownStatuses: [...prevState.reminderContext.shownStatuses, statusName],
          showExpired: prevState.reminderContext.showExpired
        }
      }));
    } else if(!checked && this.state.reminderContext.shownStatuses.includes(statusName)) {
      this.setState(prevState => ({
        reminderContext: {
          shownStatuses: prevState.reminderContext.shownStatuses.filter(s => s !== statusName),
          showExpired: prevState.reminderContext.showExpired
        }
      }));
    }
  }
  checkExpireFilter(event) {
    var checked = event.target.checked;
    if(checked && !this.state.reminderContext.showExpired) {
      this.setState(prevState => ({
        reminderContext: {
          shownStatuses: prevState.reminderContext.shownStatuses,
          showExpired: true
        }
      }));
    } else if(!checked && this.state.reminderContext.showExpired) {
      this.setState(prevState => ({
        reminderContext: {
          shownStatuses: prevState.reminderContext.shownStatuses,
          showExpired: false
        }
      }));
    }
  }
  componentDidMount() {
    UserService.getReminders().then(
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
        // for(const prop in error.response) console.log(`${prop}: ${error[prop]}`)
        if (
          !error.response ||
          (error.response && [401, 403].includes(error.response.status)) 
	) {
          EventBus.dispatch("logout");
        }
      }
    );
  }
  render() {
    var styles = Style(window.innerWidth)
    var res = this.state.content;
    if (res === "" || typeof res === "number" || res === "unknown") {
      return (
        <div className="loader-container">
      	  <div className="spinner"></div>
        </div>
      )
    } else {
      document.getElementById('headerButtons').style.display = "block";
      var statuses = [
        { value: "Attivo", label: "Attivo", disabled: false },
        { value: "Ignorato", label: "Ignorato", disabled: false },
        { value: "Archiviato", label: "Archiviato", disabled: false },
        { value: "Approvato", label: "Approvato", disabled: true },
      ];
      var sortedReminders = "";
      var filterBar =  (
        <div style={styles.filterContainer}>
          <div style={styles.filterButtonName} onClick={this.handleFilterButton}>Mostra filtri</div>
        </div>
      );
      if(this.state.showFilter) {
        var shownStatuses = this.state.reminderContext.shownStatuses
        filterBar = (
          <div style={styles.filterContainer}>
            <div style={styles.filterButtonName} onClick={this.handleFilterButton}>Nascondi filtri</div>
            <div style={styles.filterStatusContent}>
              <div style={styles.filterStatusItem}>
                <div style={styles.filterStatusLabel}>Attive</div>
                <input
                  type="checkbox"
                  checked={shownStatuses.includes("Attivo")}
                  onChange={this.checkStatusFilter}
                  style={styles.filterStatusCheck}
		  id="Attivo"
		/>
              </div>
              <div style={styles.filterStatusItem}>
                <div style={styles.filterStatusLabel}>Ignorate</div>
                <input
                  type="checkbox"
                  checked={shownStatuses.includes("Ignorato")}
                  onChange={this.checkStatusFilter}
                  style={styles.filterStatusCheck}
                 id="Ignorato"
              />
              </div>
              <div style={styles.filterStatusItem}>
                <div style={styles.filterStatusLabel}>Archiviate</div>
                <input
                  type="checkbox"
                  checked={shownStatuses.includes("Archiviato")}
                  onChange={this.checkStatusFilter}
                  style={styles.filterStatusCheck}
                  id="Archiviato"
              />
              </div>
              <div style={styles.filterStatusItem}>
                <div style={styles.filterStatusLabel}>Approvate</div>
                <input
                  type="checkbox"
                  checked={shownStatuses.includes("Approvato")}
                  onChange={this.checkStatusFilter}
                  style={styles.filterStatusCheck}
		  id="Approvato"
		/>
              </div>
            </div>
            <div style={styles.filterExpiringContent}>
              <div style={styles.filterStatusItem}>
                <div style={styles.filterStatusLabel}>Scadute</div>
                <input
                  type="checkbox"
                  checked={this.state.reminderContext.showExpired}
                  onChange={this.checkExpireFilter}
                  style={styles.filterStatusCheck}
		  id="Scaduto"
		/>
              </div>
            </div>
          </div>
        );
      }
      if(typeof(this.state.content.reminders) != "string") {
        sortedReminders = this.state.content.reminders
          .sort((a, b) => (a.expire_date > b.expire_date) ? 1 : -1)
          .map(reminder => {
             return (
               <Reminder
                 key={reminder.id}
                 reminder={reminder}
                 statuses={statuses}
                 context={this.state.reminderContext}
               />
             );
          });
        this.state.content.reminders.forEach(reminder => {
          statuses.forEach(s => {
            if(reminder.status === s.value) {
              s.disabled = true;
	    } 
          });
        });
      } else {
        sortedReminders = "Errore nell'aggiornamento delle scadenze";
      }
      return (
        <div>
          {filterBar}
          {sortedReminders}
        </div>
      );
    }
  }
}
function Style(windowWidth) {
  const perc = windowWidth / 100;
  return {
    filterContainer : {
      backgroundColor: "#BBBBBB",
      marginTop: perc * 5,
      margin: "auto",
      width: perc * 70,
      padding: perc,
      borderRadius: perc * 3
    },
    filterButtonName : {
      height: perc * 7,
      color: "#FFFFFF",
      fontFamily: "Staatliches-Regular",
      fontSize: perc * 6,
      textAlign: "center",
      cursor: "pointer",
    },
    filterStatusContent : {
      margin: perc,
      position: "relative",
      height: "100%",
    },
    filterExpiringContent : {
      margin: perc,
      position: "relative",
      height: "100%",
    },
    filterStatusItem : {
      display: "flex",
      justifyContent: "space-between",
      height: perc * 10,
      width: perc * 60,
    },
    filterStatusLabel : {
      margin: "auto",
      color: "#FFFFFF",
      fontFamily: "URWGothic-Book",
      fontSize: perc * 3.5,
    },
    filterStatusCheck : {
      margin: "auto",
      marginRight: perc * 6,
      height: perc * 4,
      width: perc * 4,
    },
    container : {
      margin: perc * 5,
      borderRadius: perc * 6,
    },
    collapsed: {
      padding: perc * 1,
      height: perc * 44,
    },
    expanded: {
      height: perc * 100,
      overflow: "scroll"
    },
    expandedContent: {
      padding: perc * 1,
    },
    reminderSeparator: {
      margin: perc * 8,
      overflow: "hidden"
      // height: perc * 100
    },
    icon: {
      position: "relative",
      width: perc * 30,
      top: perc * -38,
      left: perc * 7.5
    },
    title: {
      position: "relative",
      height: perc * 10,
      top: perc * -66,
      left: perc * 33,
      width: perc * 50,
      fontFamily: "Staatliches-Regular",
      fontSize: perc * 7,
      textAlign: "center",
      color: "#FFFFFF"
    },
    expireDate: {
      position: "relative",
      overflow: "visible",
      height: perc * 10,
      top: perc * -59,
      left: perc * 33,
      width: perc * 50,
      fontFamily: "Staatliches-Regular",
      fontSize: perc * 7,
      textAlign: "center",
      color: "#FFFFFF"
    },
    sectionName: {
      position: "relative",
      top: perc * 4,
      height: perc * 20,
      width: "100%",
      fontFamily: "Staatliches-Regular",
      fontSize: perc * 6,
      textAlign: "center",
      color: "#FFFFFF"
    },
    titleSide: {
      position: "relative",
      top: perc * 15,
      height: perc * 20,
      width: "60%",
      fontFamily: "Staatliches-Regular",
      fontSize: perc * 6,
      textAlign: "center",
      color: "#FFFFFF"
    },
    listboxDiv: {
      position: "relative",
      top: perc * -23,
      height: perc * 20,
      display: "block",
      marginLeft: "auto",
      marginRight: "auto",
      width: "90%",
      fontFamily: "Staatliches-Regular",
      fontSize: perc * 6,
      textAlign: "center",
    },
    contentTop: {
      width: "100%",
      height: perc * 10
    },
    dots: {
      display: "flex",
      justifyContent: "space-between",
      position: "relative",
      height: perc * 3,
      top: perc * -58,
      left: perc * 50,
      width: perc * 16,
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
    descriptionBox: {
      position: "relative",
      top: perc * -50,
      left: perc * 5,
      width: perc * 80,
      overflow: "scroll",
      fontFamily: "URWGothic-Book",
      fontSize: perc * 3.5,
      color: "#FFFFFF"
    },
    downloadBox: {
      position: "relative",
      top: perc * -50,
      marginTop: perc * 5,
      //left: perc * 5,
      overflow: "hidden",
      color: "#FFFFFF"
    },
    downloadName: {
      position: "relative",
      top: perc * -5,
      left: perc * 3,
      fontFamily: "URWGothic-Book",
      color: "white",
      textDecoration: "none",
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
    uploadItem: {
      display: "flex",
      position: "relative",
      //left: perc * 2,
      overflow: "hidden",
      fontFamily: "URWGothic-Book",
    },
    noDecoration: {
      textDecoration: "none",
    }
  }
};
