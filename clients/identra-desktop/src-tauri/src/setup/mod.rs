use std::time::Duration;
use tauri::AppHandle;
use tokio::time::sleep;

pub fn init(_app: &AppHandle) {
    tauri::async_runtime::spawn(async move {
        loop {
            match reqwest::get("http://127.0.0.1:8000/health").await {
                Ok(res) if res.status().is_success() => {
                    println!("[watchdog] Brain service is healthy");
                }
                _ => {
                    println!("[watchdog] Brain service is unresponsive, needs restart...");
                    // TODO: trigger python restart
                }
            }
            sleep(Duration::from_secs(5)).await;
        }
    });
}
