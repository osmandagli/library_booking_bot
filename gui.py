import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from main import BookingBot  # import your Selenium bot

CONFIG_PATH = "config.json"

START_HOUR = 9
END_HOUR = 23


def load_config():
    """
    Load full config from config.json.

    Returns:
      cfg                  -> full config dict
      library_name         -> cfg["library"]
      service_names        -> list(cfg["services"].keys())
      default_service      -> cfg["service"]
      duration_options     -> sorted list of duration hour strings
      default_duration_hr  -> cfg["duration_hours"] as string (or None)
      user_name            -> cfg["user_info"]["name"]
      user_email           -> cfg["user_info"]["email"]
      user_cf              -> cfg["user_info"]["codice_fiscale"]
      start_hour_default   -> int (from cfg["preferred_time"] if possible)
      finish_hour_default  -> int (from cfg["preferred_time"] if possible)
    """
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", f"Cannot find {CONFIG_PATH}")
        raise
    except json.JSONDecodeError as e:
        messagebox.showerror("Error", f"Invalid JSON in {CONFIG_PATH}:\n{e}")
        raise

    library_name = cfg.get("library", "")

    services_map = cfg.get("services", {})
    service_names = list(services_map.keys())
    default_service = cfg.get("service")

    durations_map = cfg.get("durations", {})
    duration_options = sorted(durations_map.keys(), key=lambda x: int(x))

    duration_hours_value = cfg.get("duration_hours")
    default_duration_hr = str(duration_hours_value) if duration_hours_value is not None else None

    user_info = cfg.get("user_info", {})
    user_name = user_info.get("name", "")
    user_email = user_info.get("email", "")
    user_cf = user_info.get("codice_fiscale", "")

    # preferred_time is like "21:00 - 22:00"
    preferred_time_str = cfg.get("preferred_time", "")
    start_hour_default = START_HOUR
    finish_hour_default = START_HOUR + 1

    try:
        if "-" in preferred_time_str:
            left, right = preferred_time_str.split("-", 1)
            left = left.strip()
            right = right.strip()
            sh = int(left.split(":")[0])
            fh = int(right.split(":")[0])
            if START_HOUR <= sh < END_HOUR:
                start_hour_default = sh
            if START_HOUR < fh <= END_HOUR:
                finish_hour_default = fh
    except Exception:
        pass

    # If we have duration_hours, try to recompute finish if needed
    if duration_hours_value is not None:
        try:
            candidate_finish = start_hour_default + int(duration_hours_value)
            if START_HOUR < candidate_finish <= END_HOUR:
                finish_hour_default = candidate_finish
        except Exception:
            pass

    return (
        cfg,
        library_name,
        service_names,
        default_service,
        duration_options,
        default_duration_hr,
        user_name,
        user_email,
        user_cf,
        start_hour_default,
        finish_hour_default,
    )


def save_selected_values(
    cfg,
    selected_service,
    start_hour_str,
    finish_hour_str,
    duration_str,
    user_name,
    user_email,
    user_cf,
):
    """
    Save chosen service, start/finish/duration and user info into config.json.

    We keep preferred_time in the format "HH:MM - HH:MM".
    """
    services_map = cfg.get("services", {})
    if selected_service not in services_map:
        messagebox.showerror(
            "Error",
            f"Selected service '{selected_service}' is not in config['services']."
        )
        return False

    # Parse and validate start/finish/duration
    try:
        start_hour = int(start_hour_str)
        finish_hour = int(finish_hour_str)
        duration_hours = int(duration_str)
    except ValueError:
        messagebox.showerror("Error", "Start, finish and duration must be integers.")
        return False

    if not (START_HOUR <= start_hour < END_HOUR):
        messagebox.showerror(
            "Error",
            f"Start hour must be between {START_HOUR} and {END_HOUR - 1}."
        )
        return False

    if not (START_HOUR < finish_hour <= END_HOUR):
        messagebox.showerror(
            "Error",
            f"Finish hour must be between {START_HOUR + 1} and {END_HOUR}."
        )
        return False

    if finish_hour <= start_hour:
        messagebox.showerror(
            "Error",
            "Finish hour must be strictly greater than start hour."
        )
        return False

    actual_duration = finish_hour - start_hour
    if actual_duration != duration_hours:
        messagebox.showerror(
            "Error",
            f"Duration mismatch:\n"
            f"  finish - start = {actual_duration} hour(s)\n"
            f"  selected duration = {duration_hours} hour(s)."
        )
        return False

    durations_map = cfg.get("durations", {})
    if str(duration_hours) not in durations_map:
        messagebox.showerror(
            "Error",
            f"Selected duration {duration_hours} hour(s) is not valid in config['durations']."
        )
        return False

    # Basic sanity checks for user info
    if not user_name.strip():
        messagebox.showwarning("Warning", "Please enter your name.")
        return False
    if not user_email.strip():
        messagebox.showwarning("Warning", "Please enter your email.")
        return False
    if not user_cf.strip():
        messagebox.showwarning("Warning", "Please enter your codice fiscale.")
        return False

    # Update config
    cfg["service"] = selected_service
    cfg["duration_hours"] = duration_hours
    # preferred_time as "HH:MM - HH:MM"
    cfg["preferred_time"] = f"{start_hour:02d}:00 - {finish_hour:02d}:00"

    cfg["user_info"] = {
        "name": user_name.strip(),
        "email": user_email.strip(),
        "codice_fiscale": user_cf.strip(),
    }

    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save {CONFIG_PATH}:\n{e}")
        return False

    return True


def main():
    root = tk.Tk()
    root.title("Library Booking Configuration")

    root.geometry("900x650")
    root.minsize(900, 650)
    root.resizable(True, True)

    (
        cfg,
        library_name,
        service_names,
        default_service,
        duration_options,
        default_duration_hr,
        user_name_default,
        user_email_default,
        user_cf_default,
        start_hour_default,
        finish_hour_default,
    ) = load_config()

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    center_frame = ttk.Frame(main_frame)
    center_frame.pack(expand=True)

    title_label = ttk.Label(
        center_frame,
        text="Configure your Library Booking",
        font=("Segoe UI", 16, "bold")
    )
    title_label.pack(pady=(0, 10), anchor="center")

    subtitle_label = ttk.Label(
        center_frame,
        text=(
            "Select service, start time, finish time and duration.\n"
            'preferred_time in config.json will be saved as "HH:MM - HH:MM".'
        ),
        justify="center"
    )
    subtitle_label.pack(pady=(0, 20), anchor="center")

    # Library
    lib_frame = ttk.Frame(center_frame)
    lib_frame.pack(pady=(0, 20))

    ttk.Label(
        lib_frame,
        text="Library:",
        font=("Segoe UI", 11, "bold")
    ).pack(side="left", padx=(0, 8))

    ttk.Label(
        lib_frame,
        text=library_name,
        font=("Segoe UI", 11)
    ).pack(side="left")

    # Service dropdown
    svc_frame = ttk.Frame(center_frame)
    svc_frame.pack(pady=(0, 20))

    ttk.Label(svc_frame, text="Service:").pack(anchor="center")

    selected_service = tk.StringVar()
    svc_combo = ttk.Combobox(
        svc_frame,
        textvariable=selected_service,
        values=service_names,
        state="readonly",
        width=70,
    )
    svc_combo.pack(pady=(5, 0))

    if default_service in service_names:
        svc_combo.set(default_service)
    elif service_names:
        svc_combo.current(0)

    # Time configuration
    time_frame = ttk.Labelframe(center_frame, text="Time configuration")
    time_frame.pack(pady=(10, 20), ipadx=10, ipady=10)

    for i in range(2):
        time_frame.columnconfigure(i, weight=1)

    # Start hour
    ttk.Label(
        time_frame,
        text=f"Start hour ({START_HOUR}–{END_HOUR - 1}):"
    ).grid(row=0, column=0, sticky="e", padx=5, pady=5)

    start_hour_var = tk.StringVar(value=str(start_hour_default))
    start_values = [str(h) for h in range(START_HOUR, END_HOUR)]

    start_hour_combo = ttk.Combobox(
        time_frame,
        textvariable=start_hour_var,
        values=start_values,
        state="readonly",
        width=10,
    )
    start_hour_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)

    # Finish hour
    ttk.Label(
        time_frame,
        text=f"Finish hour ({START_HOUR + 1}–{END_HOUR}):"
    ).grid(row=1, column=0, sticky="e", padx=5, pady=5)

    finish_hour_var = tk.StringVar(value=str(finish_hour_default))
    finish_values = [str(h) for h in range(START_HOUR + 1, END_HOUR + 1)]

    finish_hour_combo = ttk.Combobox(
        time_frame,
        textvariable=finish_hour_var,
        values=finish_values,
        state="readonly",
        width=10,
    )
    finish_hour_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    # Duration dropdown
    ttk.Label(
        time_frame,
        text="Duration (hours):"
    ).grid(row=2, column=0, sticky="e", padx=5, pady=5)

    duration_var = tk.StringVar(
        value=default_duration_hr if default_duration_hr in duration_options else ""
    )

    duration_combo = ttk.Combobox(
        time_frame,
        textvariable=duration_var,
        values=duration_options,
        state="readonly",
        width=10,
    )
    duration_combo.grid(row=2, column=1, sticky="w", padx=5, pady=5)

    # Summary label
    ttk.Label(
        time_frame,
        text="Summary:"
    ).grid(row=3, column=0, sticky="e", padx=5, pady=5)

    summary_var = tk.StringVar(value="-")

    summary_label = ttk.Label(
        time_frame,
        textvariable=summary_var,
        font=("Segoe UI", 10, "italic")
    )
    summary_label.grid(row=3, column=1, sticky="w", padx=5, pady=5)

    def update_summary(*_):
        try:
            s = int(start_hour_var.get())
            f = int(finish_hour_var.get())
            d_str = duration_var.get()
            d = int(d_str) if d_str else None
        except ValueError:
            summary_var.set("-")
            return

        if not (START_HOUR <= s < END_HOUR) or not (START_HOUR < f <= END_HOUR):
            summary_var.set("Out of library bounds.")
            return

        if f <= s:
            summary_var.set("Finish must be greater than start.")
            return

        actual = f - s
        if d is None:
            summary_var.set(
                f"{s:02d}:00 → {f:02d}:00 = {actual} hour(s), "
                f"no duration selected yet."
            )
        else:
            if actual == d:
                summary_var.set(
                    f"{s:02d}:00 → {f:02d}:00 = {actual} hour(s), "
                    f"matches selected duration {d}."
                )
            else:
                summary_var.set(
                    f"{s:02d}:00 → {f:02d}:00 = {actual} hour(s), "
                    f"but selected duration is {d} (mismatch!)."
                )

    start_hour_var.trace_add("write", update_summary)
    finish_hour_var.trace_add("write", update_summary)
    duration_var.trace_add("write", update_summary)
    update_summary()

    # User info
    user_frame = ttk.Labelframe(center_frame, text="User information")
    user_frame.pack(pady=(10, 20), ipadx=10, ipady=10)

    for i in range(2):
        user_frame.columnconfigure(i, weight=1)

    ttk.Label(user_frame, text="Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    name_var = tk.StringVar(value=user_name_default)
    ttk.Entry(user_frame, textvariable=name_var, width=40).grid(
        row=0, column=1, sticky="w", padx=5, pady=5
    )

    ttk.Label(user_frame, text="Email:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    email_var = tk.StringVar(value=user_email_default)
    ttk.Entry(user_frame, textvariable=email_var, width=40).grid(
        row=1, column=1, sticky="w", padx=5, pady=5
    )

    ttk.Label(user_frame, text="Codice fiscale:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    cf_var = tk.StringVar(value=user_cf_default)
    ttk.Entry(user_frame, textvariable=cf_var, width=40).grid(
        row=2, column=1, sticky="w", padx=5, pady=5
    )

    # Buttons
    btn_frame = ttk.Frame(center_frame)
    btn_frame.pack(pady=(20, 0))

    status_var = tk.StringVar(value="Idle")

    status_label = ttk.Label(
        btn_frame,
        textvariable=status_var,
        font=("Segoe UI", 10, "italic")
    )
    status_label.pack(side="left", padx=10)

    def run_bot_in_background():
        """Run BookingBot in a separate thread."""
        try:
            bot = BookingBot(CONFIG_PATH)
            bot.run()
            root.after(
                0,
                lambda: (
                    status_var.set("Booking finished successfully."),
                    messagebox.showinfo("Booking", "Booking completed successfully.")
                ),
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            root.after(
                0,
                lambda: (
                    status_var.set("Error during booking."),
                    messagebox.showerror("Booking error", f"An error occurred:\n{e}")
                ),
            )

    def on_save_and_run():
        svc = selected_service.get()
        s = start_hour_var.get()
        f = finish_hour_var.get()
        d = duration_var.get()
        user_name = name_var.get()
        user_email = email_var.get()
        user_cf = cf_var.get()

        if not svc:
            messagebox.showwarning("Warning", "Please select a service.")
            return
        if not s or not f or not d:
            messagebox.showwarning("Warning", "Please select start, finish and duration.")
            return

        ok = save_selected_values(
            cfg,
            svc,
            s,
            f,
            d,
            user_name,
            user_email,
            user_cf,
        )
        if ok:
            messagebox.showinfo("Saved", "Configuration saved successfully.\nStarting booking...")
            status_var.set("Running booking...")
            # Start Selenium bot in background thread
            thread = threading.Thread(target=run_bot_in_background, daemon=True)
            thread.start()

    ttk.Button(btn_frame, text="Save & Start Booking", command=on_save_and_run).pack(
        side="left", padx=10
    )
    ttk.Button(btn_frame, text="Exit", command=root.destroy).pack(
        side="left", padx=10
    )

    root.mainloop()


if __name__ == "__main__":
    main()

