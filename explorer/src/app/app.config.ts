import { ApplicationConfig, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';
import { MqttModule, MqttServiceConfig } from 'ngx-mqtt';
import {
  IMqttMessage,
  IMqttServiceOptions,
  MqttService,
  IPublishOptions,
} from 'ngx-mqtt';
import { routes } from './app.routes';

export const MQTT_SERVICE_OPTIONS: IMqttServiceOptions = {
  hostname: 'localhost',
  port: 9001,
  path: '/mqtt'
};

export const appConfig: ApplicationConfig = {
  providers: [provideRouter(routes), importProvidersFrom(MqttModule.forRoot(MQTT_SERVICE_OPTIONS))]
};


