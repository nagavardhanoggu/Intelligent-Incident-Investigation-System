import { Component, ElementRef, OnDestroy, QueryList, ViewChildren, computed, inject, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { AuthService } from '../../core/services/auth.service';
import { ThemeService } from '../../core/services/theme.service';

type ResetStep = 'email' | 'otp' | 'password' | 'done';

@Component({
  selector: 'app-forgot-password',
  imports: [
    ReactiveFormsModule,
    RouterLink,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
  ],
  templateUrl: './forgot-password.component.html',
  styleUrl: './forgot-password.component.scss',
})
export class ForgotPasswordComponent implements OnDestroy {
  @ViewChildren('otpDigitInput') private otpDigitInputs!: QueryList<ElementRef<HTMLInputElement>>;

  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private resendCooldownTimer: ReturnType<typeof setTimeout> | undefined;
  readonly theme = inject(ThemeService);

  readonly step = signal<ResetStep>('email');
  readonly loading = signal(false);
  readonly resetError = signal('');
  readonly resetMessage = signal('');
  readonly resetEmail = signal('');
  readonly sampleOtp = signal('');
  readonly resetToken = signal('');
  readonly hideNewPassword = signal(true);
  readonly hideConfirmPassword = signal(true);
  readonly otpIndexes = [0, 1, 2, 3];
  readonly otpValues = signal(['', '', '', '']);
  readonly otpExpiresInMinutes = signal<number | null>(null);
  readonly resendCooldownSeconds = signal(0);
  readonly canResendOtp = computed(() => this.step() === 'otp' && !this.loading() && this.resendCooldownSeconds() === 0);
  readonly resendOtpLabel = computed(() => {
    const seconds = this.resendCooldownSeconds();
    return seconds > 0 ? `Resend OTP in ${seconds}s` : 'Resend OTP';
  });
  readonly themeIcon = computed(() => this.theme.isDark() ? 'light_mode' : 'dark_mode');
  readonly themeToggleLabel = computed(() => this.theme.isDark() ? 'Switch to light theme' : 'Switch to dark theme');
  readonly cardIcon = computed(() => {
    switch (this.step()) {
      case 'otp':
        return 'pin';
      case 'password':
        return 'lock_reset';
      case 'done':
        return 'verified_user';
      default:
        return 'mark_email_unread';
    }
  });
  readonly cardTitle = computed(() => {
    switch (this.step()) {
      case 'otp':
        return 'Verify OTP';
      case 'password':
        return 'Create new password';
      case 'done':
        return 'Password updated';
      default:
        return 'Forgot password?';
    }
  });
  readonly cardDescription = computed(() => {
    switch (this.step()) {
      case 'otp':
        return 'Enter the 4 digit OTP sent to your registered email.';
      case 'password':
        return 'Choose and confirm the new password for your account.';
      case 'done':
        return 'Your password has been reset. You can now sign in with the new password.';
      default:
        return 'Enter your account email and we will send an OTP to reset your password.';
    }
  });
  readonly emailForm = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
  });
  readonly otpForm = this.fb.nonNullable.group({
    otp: ['', [Validators.required, Validators.pattern(/^\d{4}$/)]],
  });
  readonly passwordForm = this.fb.nonNullable.group({
    newPassword: ['', [Validators.required, Validators.minLength(8)]],
    confirmPassword: ['', [Validators.required, Validators.minLength(8)]],
  });

  otpDigit(index: number): string {
    return this.otpValues()[index] ?? '';
  }

  onOtpInput(event: Event, index: number): void {
    const input = event.target as HTMLInputElement;
    const digits = input.value.replace(/\D/g, '');

    if (digits.length > 1) {
      this.fillOtpDigits(digits, index);
      return;
    }

    const digit = digits.slice(0, 1);
    input.value = digit;
    this.setOtpDigit(index, digit);

    if (digit && index < this.otpIndexes.length - 1) {
      this.focusOtpInput(index + 1);
    }
  }

  onOtpKeydown(event: KeyboardEvent, index: number): void {
    if ((event.ctrlKey || event.metaKey) && ['a', 'c', 'v', 'x'].includes(event.key.toLowerCase())) {
      return;
    }

    if (event.key === 'ArrowLeft' && index > 0) {
      event.preventDefault();
      this.focusOtpInput(index - 1);
      return;
    }

    if (event.key === 'ArrowRight' && index < this.otpIndexes.length - 1) {
      event.preventDefault();
      this.focusOtpInput(index + 1);
      return;
    }

    if (event.key === 'Backspace') {
      event.preventDefault();
      if (this.otpDigit(index)) {
        this.setOtpDigit(index, '');
        return;
      }

      if (index > 0) {
        this.setOtpDigit(index - 1, '');
        this.focusOtpInput(index - 1);
      }
      return;
    }

    if (event.key === 'Delete') {
      event.preventDefault();
      this.setOtpDigit(index, '');
      return;
    }

    if (event.key.length === 1 && !/^\d$/.test(event.key)) {
      event.preventDefault();
    }
  }

  onOtpPaste(event: ClipboardEvent, index: number): void {
    const pasted = event.clipboardData?.getData('text') ?? '';
    const digits = pasted.replace(/\D/g, '');
    if (!digits) {
      return;
    }

    event.preventDefault();
    this.fillOtpDigits(digits, index);
  }

  requestOtp(): void {
    this.submitOtpRequest();
  }

  resendOtp(): void {
    if (!this.canResendOtp()) {
      return;
    }

    this.submitOtpRequest();
  }

  private submitOtpRequest(): void {
    if (this.emailForm.invalid) {
      this.emailForm.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.resetError.set('');
    this.resetMessage.set('');
    this.sampleOtp.set('');
    this.resetToken.set('');

    const { email } = this.emailForm.getRawValue();
    this.auth.requestPasswordReset(email).subscribe({
      next: response => {
        this.resetEmail.set(response.email ?? email.trim());
        this.sampleOtp.set(response.debugOtp ?? '');
        this.otpExpiresInMinutes.set(response.expiresInMinutes ?? null);
        this.resetMessage.set(response.message);
        this.resetOtpInput();
        this.step.set('otp');
        this.startResendCooldown();
        this.focusOtpInput(0);
        this.loading.set(false);
      },
      error: error => {
        this.resetError.set(this.errorMessage(error, 'Unable to submit the reset request. Check that the backend is running and try again.'));
        this.loading.set(false);
      },
    });
  }

  verifyOtp(): void {
    if (this.otpForm.invalid) {
      this.otpForm.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.resetError.set('');
    this.resetMessage.set('');

    const { otp } = this.otpForm.getRawValue();
    this.auth.verifyPasswordResetOtp(this.resetEmail(), otp.trim()).subscribe({
      next: response => {
        this.resetToken.set(response.resetToken);
        this.resetMessage.set(response.message);
        this.passwordForm.reset();
        this.step.set('password');
        this.clearResendCooldown();
        this.loading.set(false);
      },
      error: error => {
        this.resetError.set(this.errorMessage(error, 'Invalid OTP. Check the code and try again.'));
        this.loading.set(false);
      },
    });
  }

  confirmPasswordReset(): void {
    if (this.passwordForm.invalid || this.passwordMismatch()) {
      this.passwordForm.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.resetError.set('');
    this.resetMessage.set('');

    const { newPassword, confirmPassword } = this.passwordForm.getRawValue();
    const { otp } = this.otpForm.getRawValue();
    this.auth.confirmPasswordReset(this.resetEmail(), otp.trim(), this.resetToken(), newPassword, confirmPassword).subscribe({
      next: response => {
        this.resetMessage.set(response.message);
        this.step.set('done');
        this.loading.set(false);
      },
      error: error => {
        this.resetError.set(this.errorMessage(error, 'Unable to reset the password. Verify the OTP again and try once more.'));
        this.loading.set(false);
      },
    });
  }

  useSampleOtp(): void {
    if (!this.sampleOtp()) {
      return;
    }

    this.fillOtpDigits(this.sampleOtp(), 0);
  }

  restart(): void {
    this.step.set('email');
    this.resetError.set('');
    this.resetMessage.set('');
    this.resetEmail.set('');
    this.sampleOtp.set('');
    this.resetToken.set('');
    this.otpExpiresInMinutes.set(null);
    this.clearResendCooldown();
    this.resetOtpInput();
    this.passwordForm.reset();
  }

  ngOnDestroy(): void {
    this.clearResendCooldown();
  }

  passwordMismatch(): boolean {
    const { newPassword, confirmPassword } = this.passwordForm.getRawValue();
    return Boolean(confirmPassword && newPassword !== confirmPassword);
  }

  toggleTheme(): void {
    this.theme.toggle();
  }

  private errorMessage(error: unknown, fallback: string): string {
    if (error instanceof HttpErrorResponse) {
      const detail = error.error?.detail;
      if (typeof detail === 'string') {
        if (detail.toLowerCase().includes('email not found')) {
          return 'Email not found.';
        }

        return detail;
      }
    }

    return fallback;
  }

  private setOtpDigit(index: number, digit: string): void {
    const values = [...this.otpValues()];
    values[index] = digit;
    this.syncOtpValues(values);
  }

  private fillOtpDigits(value: string, startIndex: number): void {
    const digits = value.replace(/\D/g, '').slice(0, this.otpIndexes.length - startIndex).split('');
    if (!digits.length) {
      return;
    }

    const values = [...this.otpValues()];
    digits.forEach((digit, offset) => {
      values[startIndex + offset] = digit;
    });

    this.syncOtpValues(values);
    this.focusOtpInput(Math.min(startIndex + digits.length, this.otpIndexes.length - 1));
  }

  private syncOtpValues(values: string[]): void {
    const nextValues = this.otpIndexes.map(index => values[index] ?? '');
    this.otpValues.set(nextValues);
    this.otpForm.controls.otp.setValue(nextValues.join(''));
    this.otpForm.controls.otp.markAsDirty();
    this.otpForm.controls.otp.markAsTouched();
    this.resetError.set('');
  }

  private resetOtpInput(): void {
    this.otpValues.set(this.otpIndexes.map(() => ''));
    this.otpForm.reset();
  }

  private focusOtpInput(index: number): void {
    setTimeout(() => this.otpDigitInputs?.get(index)?.nativeElement.focus());
  }

  private startResendCooldown(seconds = 1): void {
    this.clearResendCooldown();
    this.resendCooldownSeconds.set(seconds);
    this.resendCooldownTimer = setTimeout(() => {
      this.resendCooldownSeconds.set(0);
      this.resendCooldownTimer = undefined;
    }, seconds * 1000);
  }

  private clearResendCooldown(): void {
    if (this.resendCooldownTimer) {
      clearTimeout(this.resendCooldownTimer);
      this.resendCooldownTimer = undefined;
    }
    this.resendCooldownSeconds.set(0);
  }
}
