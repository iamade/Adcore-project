import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Payment } from '../models/payment.model';  // Import the model
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class PaymentsService {
  private baseUrl = `${environment.apiUrl}/payments`;

  constructor(private http: HttpClient) {}

  getPayments(query?: string, page: number = 1, limit: number = 10): Observable<Payment[]> {
    let url = `${this.baseUrl}?page=${page}&limit=${limit}`;
    if (query) url += `&${query}`;
    return this.http.get<Payment[]>(url);
  }
  // getPayments(page: number = 1, limit: number = 10): Observable<Payment[]> {
  //   return this.http.get<Payment[]>(`${this.baseUrl}?page=${page}&limit=${limit}`);
  // }

  getPaymentById(id: string): Observable<Payment> {
    return this.http.get<Payment>(`${this.baseUrl}/by-id/${id}`);
  }

  createPayment(payment: Payment): Observable<Payment> {
    return this.http.post<Payment>(this.baseUrl, payment);
  }

  updatePayment(id: string, payment: Payment): Observable<any> {
    return this.http.put(`${this.baseUrl}/${id}`, payment);
  }

  deletePayment(id: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${id}`);
  }

  /**
   * Search payments by payee name or email
   * @param searchTerm - The search term to filter payments
   * @returns Observable of filtered payments
   */
  searchPayments(searchTerm: string): Observable<{ payments: Payment[] }> {
    const url = `${this.baseUrl}/search?payee_first_name=${searchTerm}`;
    return this.http.get<{ payments: Payment[] }>(url);
  }
}
