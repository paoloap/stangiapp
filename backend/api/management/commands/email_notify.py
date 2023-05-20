from datetime import date, timedelta
from smtplib import SMTPException
from django.template.loader import render_to_string
from django.core.mail import mail_admins, send_mail, send_mass_mail
from django.core.management import BaseCommand
#from django.conf import settings

from api.models import Reminder, ReminderStatus

today = date.today()


class Command(BaseCommand):
    help = "Send e-mail notifications related to reminders"

    def handle(self, *args, **options):
        time_settings = [30, 15, 7, 3, 2, 1]
        for n in time_settings:
            target_date = today + timedelta(days=n)
            subject = f"Hai una scadenza tra {n} giorni"
            active_status = ReminderStatus.objects.get(name="Attivo")
            reminders = Reminder.objects.filter(
                expire_date=target_date,
                status=active_status
            )
            if reminders:
                emails_list = []
                for r in reminders:
                    email_template_name = "../templates/notifications/email_template.txt"
                    c = {
                        "user": r.user.first_name,
                        "target_date": target_date.strftime("%d/%m/%Y"),
                        "reminder_title": r.title,
                    }
                    message = render_to_string(email_template_name, c)
                    #message = f"Ciao {r.user.first_name},\nti ricordo che in data {target_date.strftime('%d/%m/%Y')} scadranno i termini del seguente pagamento: {r.title}. Accedi a StangiApp per ulteriori dettagli."
                    #mail_admins(subject=subject, message=message, html_message=None)
                    emails_list.append((
                        subject,
                        message,
                        None,
                        [r.user.email],
                    ))
                emails_tuple = tuple(emails_list)
                if len(emails_tuple) > 0:
                    try:
                        send_mass_mail(emails_tuple, fail_silently=False)
                    except SMTPException as e:
                        self.stdout.write(f"------- ERRORS: ------\n{e}")
                        mail_admins(
                            subject=f"Errori in invio notifiche - {today.strftime('%d/%m/%Y')}",
                            message=f"{e}",
                            html_message=f"{e}"
                        )
            else:
                self.stdout.write(f"No notification email to send for reminders expiring in {n}")
                self.stdout.write(f"{target_date}  {active_status}")

