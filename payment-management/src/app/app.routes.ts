import { Routes } from '@angular/router';
import { PaymentsComponent } from './components/payment-list/payment-list.component';
import { AddPaymentComponent } from './components/payment-add/payment-add.component';
import { EditPaymentComponent } from './components/payment-edit/payment-edit.component';

export const routes: Routes = [
    { path: '', component: PaymentsComponent },
    { path: 'add-payment', component: AddPaymentComponent },
    { path: 'edit-payment/:id', component: EditPaymentComponent },
];
