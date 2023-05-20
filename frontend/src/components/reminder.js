import React, { Component } from 'react';
import SwipeableViews from 'react-swipeable-views';
import ReminderSeparator from '../assets/svg/reminderseparator';
import AttachDoc from '../assets/svg/attachdoc';
import AttachedDoc from '../assets/svg/attacheddoc';
import SwiperDots from './swiperdots.component';
import TypeIcon from './typeicon.component.js';
import Select from 'react-select';
import Swal from 'sweetalert2';
import UserService from "../services/user.service";
import EventBus from "../common/EventBus";


class Reminder extends Component {
  constructor(props) {
    super(props)
    this.state = {
      expanded: false,
      index: 1,
      status: props.reminder.status,
      attachments: props.reminder.up,
      //fromAttachPage : props.reminder.from_attach_page,
      statuses: props.statuses,
      shown: true
    }
    this.myRef = React.createRef();
    this.expand = this.expand.bind(this);
    this.collapse = this.collapse.bind(this);
    this.handleChangeIndex = this.handleChangeIndex.bind(this);
    this.handleSelect = this.handleSelect.bind(this);
    this.hide = this.hide.bind(this);
    this.show = this.show.bind(this);
  }
  show() {
    this.setState({ shown: true, index: 1});
  }
  hide() {
    this.setState({ shown: false});
  }
  expand() {
    this.setState({ expanded: true, });
  }
  collapse() {
    this.setState({ expanded: false, index: 1});
  }
  handleChangeIndex(index) {
    this.setState({ expanded: false, index: index})
  }
  handleScrollTo(event) {
    //history.push("http://10.0.0.3:190/manager/login");
    //UserService.goToAttachPage();
  }
  attachmentInfo(event, file_info, reminder_id) {
    var date_time = new Date(file_info.date_time);
    const file_name = this.sanifyFileName(file_info.name)
    Swal.fire({
      title: file_name,
      text: "Caricato in data: " + date_time + ", dimensione: " + file_info.size ,
      icon: 'info',
      confirmButtonColor: "#7FE4CC",
      confirmButtonText: 'Scarica',
      showDenyButton: true,
      denyButtonColor: "#DCBC88",
      denyButtonText: 'Cancella'
    }).then((result) => {
      if (result.isConfirmed) {
        //window.open(file_info.link);
        //window.open(window.location.protocol + "//" + window.location.host + "/api/download_attachment?reminder_id=" + reminder_id + "&repo_type=up&file_name=" + file_info.name);
        this.downloadFile(reminder_id, "up", file_info.name);
      } else if (result.isDenied) {
        Swal.fire({
          title: "Sicuro di voler cancellare il documento?",
          text: "Questa operazione non può essere annullata",
          icon: 'warning',
          showCancelButton: true,
          confirmButtonColor: "#DCBC88",
          confirmButtonText: 'Sì',
          cancelButtonColor: "#7FE4CC",
          cancelButtonText: 'No'
        }).then((result) => {
          if(result.isConfirmed) {
            UserService.deleteAttachment(file_info.name).then(
              response => {
                if (response.data.result === "success") {
                  this.setState(prevState => ({
                    attachments: prevState.attachments.filter(element => {
                      return element.name !== file_info.name;
                    })
		  }))
                  Swal.fire({
                    text: "il documento '" + file_info.name + "' è stato cancellato",
                    icon: "success",
                    confirmButtonColor: '#7FE4CC'
                  })
                } else {
                  Swal.fire({text: "errore nella cancellazione", icon: "error", confirmButtonColor: '#DCBC88'})
                }
              },
              error => {
                Swal.fire({text: "Errore nella cancellazione", icon: "error", confirmButtonColor: '#DCBC88'})
              }
            );
           }
        });
      }
    });
  }
  attachFile(reminder_id) {
    Swal.fire({
      title: "Allega un documento",
      icon: 'info',
      input: "file",
      confirmButtonColor: "#7FE4CC",
      confirmButtonText: 'Allega',
      showCancelButton: true,
      cancelButtonColor: "#DCBC88",
      cancelButtonText: 'Annulla'
    }).then((result) => {
      const file = result.value;
      if (file) {
        const form = new FormData();
        form.append("reminder_id", reminder_id);
        form.append("attachment", file);
        UserService.attachFile(form).then((response) => {
          if(typeof(response.data) != "string") {
            const new_attach = {
              name : response.data.name,
              size : response.data.size,
              date_time : new Date(),
	    }
            this.setState(prevState => ({
              attachments: [...prevState.attachments, new_attach]
	    }));
            Swal.fire({ title: "Documento allegato!", icon: "success" });
	  }
        });
      }
    });
  }
  downloadFile(reminder_id, repo_type, file_name) {
    UserService.downloadAttachment(
      reminder_id,
      repo_type,
      file_name
    ).then((response) => {
      // Create blob link to download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute(
        'download',
        this.sanifyFileName(file_name)
      );
      // Append to html link element page
      document.body.appendChild(link);
      // Start download
      link.click();
      // Clean up and remove the link
      link.parentNode.removeChild(link);
    });
  }
  sanifyFileName(file_name) {
    return file_name.replace(/([^_]*_){2}/, '')
  }
  handleSelect(event) {
    var msg = "";
    switch(event.value) {
      case "Attivo":
        msg = "Sicuro di voler riattivare la scadenza?";
        break;
      case "Ignorato":
        msg = "Sicuro di voler ignorare la scadenza?";
        break;
      case "Archiviato":
        msg = "Sicuro di voler archiviare la scadenza?";
        break;
      default:
    }
    Swal.fire({
      text: msg,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#7FE4CC',
      cancelButtonColor: '#DCBC88',
      confirmButtonText: 'Sì',
      cancelButtonText: 'No',
    }).then((result) => {
      if (result.isConfirmed) {
        var messages = {
          "server_error": "Errore del server, richiedi assistenza",
          "no_reminder": "La scadenza non è stata trovata",
          "status_not_found": "Lo stato inserito non è stato trovato",
          "forbidden_status": "Non è permesso inserire lo stato richiesto",
          "same_status": "La scadenza era già in questo stato",
	}
        var icon = 'success';
        var resultMsg = "Lo stato della scadenza è stato cambiato in '" + event.value + "'";
        UserService.changeReminderStatus(this.props.reminder.id, event.value).then(
          response => {
            if (!response.data.error) {
              this.setState({
                status: event.value
              });
              Swal.fire({text: resultMsg, icon: icon, confirmButtonColor: '#7FE4CC'})
            } else {
              icon = "error";
              result = messages[response.data.error];
              Swal.fire({text: result, icon: icon, confirmButtonColor: '#DCBC88'})
            }
          },
          error => {
            icon = "error";
            result = (
              error.response && ( error.response.status || error.response.data.detail)
            ) || "unknown";
            if (!error.response || (error.response && error.response.status === 401)) {
              EventBus.dispatch("logout");
            }
            Swal.fire({text: result, icon: icon, confirmButtonColor: '#DCBC88'})
          }
        );
      }
    })
  }
  componentDidMount() {
    if(this.myRef.current && this.myRef.current !== null) {
      this.myRef.current.scrollIntoView();
    }
    if(!this.props.context.shownStatuses.includes(this.state.status)) {
      this.hide();
    } else {
      this.show();
    }
  }
  componentDidUpdate(prevProps, prevState) {
    if(
      (prevProps.context.shownStatuses !== this.props.context.shownStatuses)
      || (prevProps.context.showExpired !== this.props.context.showExpired)
      || (prevState.status !== this.state.status)
    ) {
      const showExpired = this.props.context.showExpired;
      const expire_date = new Date(this.props.reminder.expire_date).getTime();
      const now_date = new Date().getTime();
      const isExpired = (now_date >= expire_date);
      const isStatusShown = this.props.context.shownStatuses.includes(this.state.status);
      if(isStatusShown && (showExpired || !isExpired)) {
        this.show();
      } else {
        this.hide();
      }
      if(prevState.status !== this.state.status) {
        this.setState({statuses : [ ...prevState.statuses.map(status => {
	  if(status.value === prevState.status) {
	    return { ...status, disabled: false }
	  } else if(status.value === this.state.status) {
	    return { ...status, disabled: true }
	  } else {
	    return status
	  }
	})]})
      }
    }
  }
  render() {
    if(this.state.shown) {
      var ref;
      if (this.state.fromAttachPage) {
        this.setState({ expanded: false, index: 0, fromAttachPage: false})
        ref = this.myRef;
      }
      var styles = Style(window.innerWidth)
      const expire_date = new Date(this.props.reminder.expire_date).getTime();
      const now_date = new Date().getTime();
      var elapsedDays = Math.trunc((expire_date - now_date) / (1000 * 3600 * 24));
      var bgcolor = "#FFFFFF"
      if(elapsedDays < 1) {
        bgcolor = "#BBBBBB";
      }
      else if(elapsedDays < 15) {
        bgcolor = "#EEACBE";
      } else if(elapsedDays < 60) {
        bgcolor = "#DCBC88";
      } else if(elapsedDays < 90) {
        bgcolor = "#B7DA72";
      } else {
        bgcolor = "#7FE4CC";
      }
      var instanceStyle = {
        backgroundColor: bgcolor
      }
      const customStyles = {
        option: provided => ({
          ...provided,
          color: bgcolor,
          opacity: 0.7,
          border: "0",
          zIndex: 9999
        }),
        control: provided => ({
          ...provided,
          color: bgcolor,
          opacity: 0.7,
          border: "0",
          zIndex: 9999
        }),
        singleValue: (provided) => ({
          ...provided,
          color: bgcolor,
          opacity: 0.7,
          border: "0",
          zIndex: 9999
        })
      }
      if (this.state.expanded) {
          var download_list = [];
          this.props.reminder.down.forEach(element => {
            const file_name = this.sanifyFileName(element.name)
            download_list.push(
              <div style={styles.downloadItem}>
                <div
                  style={styles.noDecoration}
                  onClick={() => { this.downloadFile(this.props.reminder.id, "down", element.name)}}
                >
                  <AttachedDoc height={styles.myAttaches.height} />
                  <span style={styles.downloadName}>{file_name}</span>
                </div>
              </div> 
            )
          });
          return (
            <div
              style={Object.assign({}, instanceStyle, styles.container, styles.expanded)}
            >
              <div style={styles.expandedContent}>
                <div style={styles.reminderSeparator}>
                  <ReminderSeparator />
                </div>
                <div style={styles.icon} onClick={this.collapse}>
                  <TypeIcon name={this.props.reminder.type}/>
                </div>
                <div style={styles.title}>{this.props.reminder.title}</div>
                <div style={styles.expireDate}>{this.props.reminder.expire_date}</div>
                <div style={styles.descriptionBox}>{this.props.reminder.description}</div>
                <div style={styles.downloadBox}>{download_list}</div>
              </div>
            </div>
          );
      } else {
        var upload_list = [];
        const attachmentsByDate = this.state.attachments.sort(
          (objA, objB) => Number(objA.date_time) - Number(objB.date_time),
        );
        attachmentsByDate.forEach(element => {
          upload_list.push(
            <div style={styles.uploadItem} onClick={e => this.attachmentInfo(e, element, this.props.reminder.id)}>
              <AttachedDoc height={styles.myAttaches.height} />
            </div> 
          )
        });
        upload_list.push(
          <div onClick={e => this.attachFile(this.props.reminder.id)}>
            <AttachDoc height={styles.myAttaches.height} />
          </div>
        );
        return (
          <div ref={ref} style={Object.assign({}, instanceStyle, styles.container, styles.collapsed)} >
            <SwipeableViews
              enableMouseEvents
              index={this.state.index}
              onChangeIndex={index => this.handleChangeIndex(index)} 
            >
              <div>
                <div style={styles.sectionName}>Allega documenti</div>
                <div style={styles.titleSide}>{this.props.reminder.title}</div>
                <div style={styles.myAttaches}>
                  {upload_list}
                </div>
              </div>
              <div>
                  <div style={styles.reminderSeparator}>
                    <ReminderSeparator />
                  </div>
                  <div style={styles.icon} onClick={this.expand}>
                    <TypeIcon name={this.props.reminder.type}/>
                  </div>
                  <div style={styles.title}>{this.props.reminder.title}</div>
                  <div style={styles.expireDate}>{this.props.reminder.expire_date}</div>
              </div>
              <div>
                <div style={styles.sectionName}>Cambia stato alla scadenza</div>
                <div style={styles.titleSide}>{this.props.reminder.title}</div>
                <div style={styles.listboxDiv}>
                  <Select
                    options={this.state.statuses}
                    isSearchable={ false }
                    isOptionDisabled={(option) => option.disabled}
                    value = {
                      this.state.statuses.filter(status => 
                        status.value === this.state.status
                      )
                    }
                    onChange={this.handleSelect}
                    styles={customStyles}
                    menuPortalTarget={document.body} 
                  />
                </div>
              </div>
            </SwipeableViews>
            <SwiperDots selected={this.state.index} style={styles.dots}/>
          </div>
        );
      }
    } else {   
      return ""
    }
  }
}

function Style(windowWidth) {
  const perc = windowWidth / 100;
  return {
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



// function Reminder(props) {
//   return (
//     <SwipeableViews enableMouseEvents index="1">
//       <div style={Object.assign({}, styles.slide, styles.slide1)}>{props.reminder.expire_date}</div>
//       <div style={Object.assign({}, styles.slide, styles.slide2)}>{props.reminder.title}</div>
//       <div style={Object.assign({}, styles.slide, styles.slide3)}>{props.reminder.status}</div>
//     </SwipeableViews>
//   );
// }

export default Reminder;
