import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-severity-chip',
  template: '<span class="chip" [class]="value.toLowerCase()">{{ value }}</span>',
  styles: [
    `
      .chip {
        display: inline-flex;
        min-width: 82px;
        justify-content: center;
        border-radius: 999px;
        border: 1px solid transparent;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 700;
      }
      .critical {
        background: #fde8e8;
        color: #b42318;
      }
      .high {
        background: #fff4db;
        color: #9a5b00;
      }
      .medium {
        background: #fff1eb;
        color: #d43f1d;
      }
      .low {
        background: #e7f8ef;
        color: #087443;
      }
      :host-context(html[data-theme='dark']) .critical {
        border-color: rgba(248, 113, 113, 0.28);
        background: rgba(248, 113, 113, 0.14);
        color: #ffb4a8;
      }
      :host-context(html[data-theme='dark']) .high {
        border-color: rgba(251, 191, 36, 0.28);
        background: rgba(251, 191, 36, 0.14);
        color: #ffd36b;
      }
      :host-context(html[data-theme='dark']) .medium {
        border-color: rgba(255, 112, 74, 0.28);
        background: rgba(255, 112, 74, 0.13);
        color: #ff9b7a;
      }
      :host-context(html[data-theme='dark']) .low {
        border-color: rgba(52, 211, 153, 0.28);
        background: rgba(52, 211, 153, 0.14);
        color: #55e0ae;
      }
    `,
  ],
})
export class SeverityChipComponent {
  @Input({ required: true }) value!: string;
}
