#[tauri::command]
pub fn ping() -> String {
    println!("[ipc] received ping from frontend");
    "pong".to_string()
}

pub fn init() {
    // Other IPC init if needed
}
