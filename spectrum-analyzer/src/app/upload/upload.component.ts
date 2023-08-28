import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface Constants {
  LOWER_GREEN: number[];
  UPPER_GREEN: number[];
  LOWER_WAVE_COLOR: number[];
  UPPER_WAVE_COLOR: number[];
  KERNEL_SIZE: number[];
  DILATE_ITERATIONS: number;
  ERODE_ITERATIONS: number;
  VIDEO_PATH: string;
}

@Component({
  selector: 'app-upload',
  templateUrl: './upload.component.html',
  styleUrls: ['./upload.component.css']
})
export class UploadComponent {
  constants!: Constants;
  resultMessage = '';
  selectedFile!: File;  // Added a property to hold the selected file

  constructor(private http: HttpClient) {
    // Fetch constants on component initialization
    this.fetchConstants();
  }

  // Implement the onFileSelected method
  onFileSelected(event: any) {
    if (event.target.files && event.target.files[0]) {
      this.selectedFile = event.target.files[0];
      // You can also update the resultMessage to show the file name or any other message
      this.resultMessage = `Selected file: ${this.selectedFile.name}`;
    }
  }

  // Implement the uploadVideo method
  uploadVideo() {
    if (!this.selectedFile) {
      this.resultMessage = "No file selected!";
      return;
    }
    // Here you should handle uploading the file and analyzing it
    // Depending on your backend setup, you might use the HttpClient to send a POST request with the file
    // For now, we'll just update the message
    this.resultMessage = `Uploading and analyzing ${this.selectedFile.name}...`;
    // Later you should implement the actual upload logic
  }

  fetchConstants() {
    this.http.get<Constants>('http://localhost:5000/get_constants').subscribe(
        (data) => {
            this.constants = data;
        },
        (error) => {
            this.resultMessage = 'Error fetching constants!';
        }
    );
  }

  runWithConstants() {
      // Use constants to run the script or update the backend
      // This can be a POST request to send modified constants to the backend
      // For now, let's just log the constants
      console.log(this.constants);
  }
}