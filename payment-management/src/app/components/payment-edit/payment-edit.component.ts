import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { PaymentsService } from '../../services/payment.service';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSelectModule } from '@angular/material/select'; 
import { formatDate } from '@angular/common';

@Component({
  selector: 'app-payment-edit',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    RouterModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  templateUrl: './payment-edit.component.html',
  styleUrl: './payment-edit.component.css'
})
export class EditPaymentComponent {
  paymentForm: FormGroup;
  paymentId: string | null = null;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private paymentsService: PaymentsService
  ) {
    this.paymentForm = this.fb.group({
      payee_first_name: ['', Validators.required],
      payee_last_name: ['', Validators.required],
      payee_due_date: ['', Validators.required],
      due_amount: [0, Validators.required],
      payee_payment_status: ['', Validators.required],
      payee_address_line_1: ['', Validators.required],
      payee_city: ['', Validators.required],
      payee_postal_code: ['', Validators.required],
      payee_email: ['', [Validators.required, Validators.email]],
      payee_address_line_2: [''],
      payee_country: ['', Validators.required],
      payee_province_or_state: [''],
      payee_phone_number: ['', [Validators.required, Validators.pattern('^[+][0-9]{10,15}$')]],
      currency: ['', Validators.required],
      discount_percent: [0, [Validators.min(0), Validators.max(100)]],
      tax_percent: [0, [Validators.min(0), Validators.max(100)]],
    });
  }

  ngOnInit(): void {
    this.paymentId = this.route.snapshot.paramMap.get('id');
    if (this.paymentId) {
      this.paymentsService.getPaymentById(this.paymentId).subscribe(payment => {
          // Convert date string to Date object
          payment.payee_due_date = formatDate(payment.payee_due_date, 'yyyy-MM-dd', 'en-US');

        this.paymentForm.patchValue(payment);
      });
    }
  }


  onSubmit(): void {
    if (this.paymentForm.valid && this.paymentId) {
      const updatedPayment = {
        ...this.paymentForm.value,
        payee_due_date: formatDate(this.paymentForm.value.payee_due_date, 'yyyy-MM-dd', 'en-US')
      };

      this.paymentsService.updatePayment(this.paymentId, updatedPayment)
        .subscribe(() => {
          this.router.navigate(['/']);
        });
    }
  }
  // onSubmit(): void {
  //   if (this.paymentForm.valid && this.paymentId) {
  //     this.paymentsService.updatePayment(this.paymentId, this.paymentForm.value)
  //       .subscribe(() => {
  //         this.router.navigate(['/']);
  //       });
  //   }
  // }

}
