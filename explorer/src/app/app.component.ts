import { Component, importProvidersFrom } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import {
  IMqttMessage,
  MqttModule,
  MqttService,
  MqttServiceConfig
} from 'ngx-mqtt';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
  providers: [MqttService]
})
export class AppComponent {
  title = 'explorer';

  data: string = '';

  private subscription: Subscription;
  public message: string = '';

  constructor(private _mqttService: MqttService) {
    this.subscription = this._mqttService.observe('collect-page').subscribe((message: IMqttMessage) => {
      this.message = message.payload.toString();
    });
  }

  public unsafePublish(topic: string, message: string): void {
    this._mqttService.unsafePublish(topic, message, { qos: 1, retain: false });
  }

  public ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  publishTarget() {
    this.unsafePublish("collect-page", this.data);
  }

}
