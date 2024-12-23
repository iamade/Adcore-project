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
import { CommonModule, formatDate } from '@angular/common';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-payment-edit',
  standalone: true,
  imports: [
    CommonModule,
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
  evidenceFile: File | null = null;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private paymentsService: PaymentsService,
    private snackBar: MatSnackBar

  ) {
    this.paymentForm = this.fb.group({
      payee_first_name: ['', Validators.required],
      payee_last_name: ['', Validators.required],
      payee_payment_status: ['', Validators.required],
      payee_due_date: ['', Validators.required],
      payee_address_line_1: ['', Validators.required],
      payee_address_line_2: [''],
      payee_city: ['', Validators.required],
      payee_country: ['', Validators.required],
      payee_province_or_state: [''],
      payee_postal_code: ['', Validators.required],
      payee_phone_number: ['', [Validators.required]],
      payee_email: ['', [Validators.required, Validators.email]],
      discount_percent: [0, [Validators.min(0), Validators.max(100)]],
      tax_percent: [0, [Validators.min(0), Validators.max(100)]],
      due_amount: [0, Validators.required],
      currency: ['', Validators.required],
      
      
    });
  }

  ngOnInit(): void {
    this.paymentId = this.route.snapshot.paramMap.get('id');
    if (this.paymentId) {
      this.paymentsService.getPaymentById(this.paymentId).subscribe(payment => {
          // Convert date string to Date object
          if (payment.payee_due_date) {
            payment.payee_due_date = formatDate(payment.payee_due_date, 'yyyy-MM-dd', 'en-US');
          //  payment.payee_due_date = new Date(payment.payee_due_date);  // This ensures date picker works
          }
         

       // this.paymentForm.patchValue(payment);
        this.paymentForm.patchValue({
          payee_first_name: payment.payee_first_name,
          payee_last_name: payment.payee_last_name,
          payee_due_date: payment.payee_due_date,
          due_amount: payment.due_amount,
          payee_payment_status: payment.payee_payment_status,
          payee_address_line_1: payment.payee_address_line_1,
          payee_city: payment.payee_city,
          payee_postal_code: payment.payee_postal_code,
          payee_email: payment.payee_email,
          payee_address_line_2: payment.payee_address_line_2 || '',
          payee_country: payment.payee_country,
          payee_province_or_state: payment.payee_province_or_state || '',
          payee_phone_number: payment.payee_phone_number,
          currency: payment.currency,
          discount_percent: payment.discount_percent || 0,
          tax_percent: payment.tax_percent || 0,
  
        });

        console.log(this.paymentForm);
        
      });
    }
  }


  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.evidenceFile = input.files[0];
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
