import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { PaymentService } from '../../services/payment.service';


@Component({
  selector: 'app-payment-add',
  standalone: true,
  imports: [],
  templateUrl: './payment-add.component.html',
  styleUrl: './payment-add.component.css'
})
export class PaymentAddComponent {
  paymentForm: FormGroup;

  constructor(private fb: FormBuilder, private paymentService: PaymentService) {
    this.paymentForm = this.fb.group({
      payee_first_name: ['', Validators.required],
      payee_last_name: ['', Validators.required],
      payee_payment_status: ['pending', Validators.required],
      payee_due_date: ['', Validators.required],
      payee_address_line_1: ['', Validators.required],
      payee_city: ['', Validators.required],
      payee_country: ['', Validators.required],
      payee_postal_code: ['', Validators.required],
      payee_email: ['', [Validators.required, Validators.email]],
      currency: ['', Validators.required],
      discount_percent: [0, [Validators.min(0), Validators.max(100)]],
      tax_percent: [0, [Validators.min(0), Validators.max(100)]],
      due_amount: [0, [Validators.required, Validators.min(0)]]
    });
  }

  savePayment() {
    if (this.paymentForm.valid) {
      this.paymentService.createPayment(this.paymentForm.value).subscribe(() => {
        console.log('Payment created successfully!');
      });
    }
  }
}

