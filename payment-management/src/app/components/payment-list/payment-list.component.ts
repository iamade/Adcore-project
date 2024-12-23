import { Component, NgModule, OnInit, ViewChild } from '@angular/core';
import { PaymentsService } from '../../services/payment.service';
import { Payment } from '../../models/payment.model';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';

@Component({
  selector: 'app-payments',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule
  ],
  templateUrl: './payment-list.component.html',
})
export class PaymentsComponent implements OnInit {
  displayedColumns: string[] = ['payee_first_name', 'payee_last_name', 'total_due', 'payee_payment_status', 'actions'];
  dataSource = new MatTableDataSource<Payment>();
  payments: Payment[] = [];
  searchTerm: string = '';

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  constructor(private paymentsService: PaymentsService, private router: Router) {}

  ngOnInit(): void {
    this.loadPayments();
  }

  loadPayments(): void {
    this.paymentsService.getPayments().subscribe((data) => {
      this.dataSource = new MatTableDataSource<Payment>(data);
      this.dataSource.paginator = this.paginator;
    });
  }

  /**
   * Search payments by name or email
   */
  searchPayments(searchTerm: string) {
    this.paymentsService.searchPayments(searchTerm).subscribe((data) => {
      this.payments = data.payments;
    });
  }

    // Navigate to edit payment page
    editPayment(payment: any): void {
      this.router.navigate([`/edit-payment/${payment.id}`]);
    }
  
    // Delete payment by ID
    deletePayment(paymentId: string): void {
      if (confirm('Are you sure you want to delete this payment?')) {
        this.paymentsService.deletePayment(paymentId).subscribe(() => {
          this.loadPayments();  // Reload table after deletion
        });
      }
    }
}

