import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, computed, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';

import { AuthService } from '../../../core/services/auth.service';

interface AccessRoleData {
  scopeCards: { label: string; value: string; icon: string }[];
  permissions: { label: string; description: string; area: string; enabled: boolean }[];
  boundaries: { label: string; value: string }[];
  auditTrail: { event: string; time: string }[];
  accountStatus: string;
}

@Component({
  selector: 'app-access-role',
  imports: [DatePipe, MatCardModule, MatChipsModule, MatIconModule],
  templateUrl: './access-role.component.html',
  styleUrl: './access-role.component.scss',
})
export class AccessRoleComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1';
  readonly user = computed(() => this.auth.currentUser());

  permissions: AccessRoleData['permissions'] = [];
  scopeCards: AccessRoleData['scopeCards'] = [];
  boundaries: AccessRoleData['boundaries'] = [];
  auditTrail: AccessRoleData['auditTrail'] = [];
  accountStatus = '';

  ngOnInit(): void {
    this.http.get<AccessRoleData>(`${this.apiUrl}/account/access`).subscribe(data => {
      this.permissions = data.permissions;
      this.scopeCards = data.scopeCards;
      this.boundaries = data.boundaries;
      this.auditTrail = data.auditTrail;
      this.accountStatus = data.accountStatus;
    });
  }
}
