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
    `,
  ],
})
export class SeverityChipComponent {
  @Input({ required: true }) value!: string;
}
