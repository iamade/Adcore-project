import { Routes } from '@angular/router';

export const routes: Routes = [
    { path: '', component: PaymentsComponent },
    { path: 'add-payment', component: AddPaymentComponent },
    { path: 'edit-payment/:id', component: EditPaymentComponent },
];
