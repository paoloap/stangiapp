import api from './api';
class UserService {
  getPublicContent() {
    return api.get('/all');
  }
  getProfile() {
    return api.get("/user_profile");
  }
  getReminders() {
    return api.get("/user_reminders");
  }
  getGlobalAttachments() {
    return api.get("/global_attachments");
  }
  downloadAttachment(reminder_id, repo_type, file_name) {
    return api.get("/download_attachment", {
      params: { reminder_id: reminder_id, repo_type: repo_type, file_name: file_name },
      responseType: "blob"
    });
  }
  goToAttachPage() {
    return api.post("/go_to_attach_page");
  }
  attachFile(form) {
    return api.post("/attach_file", form);
  }
  changeReminderStatus(reminder, status) {
    return api.put("/change_reminder_status", { reminder_id: reminder, status: status });
  }
  deleteAttachment(file_name) {
    return api.delete("/delete_attachment", { data: { file_name: file_name }});
  }
  logout() {
    return api.post("/logout");
  }
}
export default new UserService();

