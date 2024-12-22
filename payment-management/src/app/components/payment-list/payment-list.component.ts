import { Component, OnInit, ViewChild } from '@angular/core';
import { PaymentsService } from '../../services/payment.service';
import { Payment } from '../../models/payment.model';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';

@Component({
  selector: 'app-payments',
  templateUrl: './payment-list.component.html',
})
export class PaymentsComponent implements OnInit {
  displayedColumns: string[] = ['payee_first_name', 'payee_last_name', 'total_due', 'payee_payment_status', 'actions'];
  dataSource = new MatTableDataSource<Payment>();
  payments: Payment[] = [];
  searchTerm: string = '';

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  constructor(private paymentsService: PaymentsService) {}

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

}

