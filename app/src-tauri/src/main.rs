// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::command;
use serde::{Deserialize, Serialize};
use reqwest::Client;

#[derive(Debug, Serialize, Deserialize)]
struct ApiResponse {
    message: Option<String>,
    data: Option<serde_json::Value>,
    error: Option<String>,
}

#[command]
async fn generate_tests(params: serde_json::Value) -> Result<ApiResponse, String> {
    let client = Client::new();
    let res = client
        .post("http://localhost:8080/generate")
        .json(&params)
        .send()
        .await
        .map_err(|e| e.to_string())?;

    res.json::<ApiResponse>()
        .await
        .map_err(|e| e.to_string())
}

#[command]
async fn crawl_website(params: serde_json::Value) -> Result<ApiResponse, String> {
    let client = Client::new();
    let res = client
        .post("http://localhost:8080/crawl")
        .json(&params)
        .send()
        .await
        .map_err(|e| e.to_string())?;

    res.json::<ApiResponse>()
        .await
        .map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![generate_tests, crawl_website])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
